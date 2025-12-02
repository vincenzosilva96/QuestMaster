import os
import json
import subprocess
import tempfile
import re
import google.generativeai as genai
from docx import Document
from dotenv import load_dotenv

class QuestMasterPhase1:
    """
    QuestMaster - Phase 1: Story Generation
    Usa Google Gemini (GenerativeModel) + Fast Downward per generare e validare un PDDL coerente.
    """

    def __init__(self, gemini_api_key=None, fast_downward_path="./fast-downward.py"):
        load_dotenv()
        self.fast_downward_path = fast_downward_path
        self.output_dir = "phase1_output"
        os.makedirs(self.output_dir, exist_ok=True)

        gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if gemini_api_key is None:
            pass

        genai.configure(api_key=gemini_api_key)
        self.model_name = "gemini-2.5-flash" 
        self.model = genai.GenerativeModel(model_name=self.model_name)

    # GENERAZIONE PDDL

    def generate_pddl(self, lore, branching, depth):
        print("StoryAgent: Generazione PDDL tramite Gemini Chat...")

        prompt = f"""
            Sei QuestMaster, un sistema di intelligenza artificiale che genera missioni narrative come problemi di pianificazione PDDL.
            Sei un esperto di pianificazione IA e PDDL. Il tuo output DEVE essere rigorosamente un singolo oggetto JSON, come richiesto.

            Storia:
            {lore}

            Branching Factor: {branching}
            Depth Constraints: {depth}

            Genera due file PDDL completi e logicamente coerenti:
            1. Un file DOMAIN con predicati e azioni.
            2. Un file PROBLEM con oggetti, init e goal.
            Aggiungi commenti che spiegano ogni sezione.

            Restituisci un file JSON con questa struttura:
            {{
            "domain": "<domain.pddl content>",
            "problem": "<problem.pddl content>"
            }}
            """
        
        response = self.model.generate_content(
            contents=prompt,
            generation_config={
                "temperature": 0.4,
                "response_mime_type": "application/json",
            }
        )

        text_output = response.text.strip()

        try:
            data = json.loads(text_output)
        except json.JSONDecodeError:
            start = text_output.find("{")
            end = text_output.rfind("}") + 1
            if start != -1 and end != -1:
                try:
                    data = json.loads(text_output[start:end])
                except json.JSONDecodeError as e:
                    print(f"Errore di parsing JSON anche dopo il ritaglio: {e}")
                    data = {}
            else:
                data = {}

        return data.get("domain", ""), data.get("problem", "")
    
    def validate_pddl(self, domain_text, problem_text):
        print("Validator: eseguo Fast Downward per la validazione...")

        with tempfile.TemporaryDirectory() as tmpdir:
            domain_path = os.path.join(tmpdir, "domain.pddl")
            problem_path = os.path.join(tmpdir, "problem.pddl")

            with open(domain_path, "w") as f:
                f.write(domain_text)
            with open(problem_path, "w") as f:
                f.write(problem_text)

            try:
                command = [
                    "python", 
                    self.fast_downward_path, 
                    domain_path, 
                    problem_path, 
                    "--search", 
                    "astar(blind())"
                ]
                
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=60,
                    check=False 
                )

                output = result.stdout + result.stderr

                if "Solution found!" in output or "Plan length" in output:
                    return True, "Piano valido trovato", output
                elif "unsolvable" in output.lower():
                    return False, "Problema logicamente irrisolvibile", output
                elif "parse error" in output.lower() or "error" in output.lower():
                    if "parse error" in output.lower():
                        return False, "Errore di sintassi nel PDDL", output
                    else:
                        return False, "Errore durante l'esecuzione di Fast Downward", output
                else:
                    return False, "Nessuna soluzione trovata (potenziale incoerenza)", output

            except subprocess.TimeoutExpired:
                return False, "Timeout del planner", ""
            except FileNotFoundError:
                return False, f"Impossibile eseguire Fast Downward. Verifica che 'python' sia nel PATH e che il percorso dello script sia corretto: {self.fast_downward_path}", ""
            except Exception as e:
                return False, f"Errore imprevisto durante l'esecuzione di Fast Downward: {str(e)}", ""
    

    def reflection_agent(self, domain_text, problem_text, error_message, planner_output):
        print("ReflectionAgent: Analisi e proposta di correzione PDDL...\n")

        prompt = f"""
            Sei l'agente di riflessione di QuestMaster. Sei un esperto di pianificazione IA e debugging PDDL.
            Il validatore Fast Downward ha segnalato un errore. Analizza e proponi modifiche ragionate.

            Errore riscontrato:
            {error_message}

            Output del planner (prime 2000 linee):
            {planner_output[:2000]}

            DOMAIN:
            {domain_text}

            PROBLEM:
            {problem_text}

            Identifica la causa probabile e genera una versione corretta dei file.
            Fornisci anche una breve spiegazione in linguaggio naturale del problema e della modifica.

            Rispondi in formato JSON con questa struttura:
            {{
            "explanation": "<breve spiegazione delle modifiche>",
            "domain": "<domain.pddl corretto>",
            "problem": "<problem.pddl corretto>"
            }}
            """

        response = self.model.generate_content(
            contents=prompt,
            generation_config={
                "temperature": 0.4,
                "response_mime_type": "application/json",
            }
        )

        text_output = response.text.strip()

        try:
            data = json.loads(text_output)
        except json.JSONDecodeError:
            start = text_output.find("{")
            end = text_output.rfind("}") + 1
            if start != -1 and end != -1:
                try:
                    data = json.loads(text_output[start:end])
                except Exception:
                    data = {}
            else:
                data = {}

        new_domain = data.get("domain", domain_text)
        new_problem = data.get("problem", problem_text)
        explanation = data.get("explanation", "Nessuna spiegazione fornita.")

        print("\n**Reflection Agent ha proposto le seguenti modifiche:**")
        print(f"Spiegazione: {explanation}\n")

        print("Vuoi visualizzare un'anteprima delle modifiche?")
        choice = input("[Y] sì, [N] no: ").strip().lower()
        if choice == "y":
            print("\n--- DOMAIN (corretto) ---")
            print(new_domain[:800] + ("..." if len(new_domain) > 800 else ""))
            print("\n--- PROBLEM (corretto) ---")
            print(new_problem[:800] + ("..." if len(new_problem) > 800 else ""))

        confirm = input("\nApprovare queste modifiche? [Y/N]: ").strip().lower()
        if confirm != "y":
            print("\nInserisci un feedback per il Reflection Agent (es. cosa migliorare, cosa mantenere):")
            feedback = input("> ")

            feedback_prompt = f"""
                L'utente ha rifiutato le modifiche precedenti e ha fornito questo feedback:
                "{feedback}"

                Analizza nuovamente i file PDDL e applica modifiche coerenti, solo se strettamente necessario.
                Rispondi in formato JSON con la stessa struttura di prima.
                """
            response2 = self.model.generate_content(
                contents=prompt + "\n\n" + feedback_prompt,
                generation_config={
                    "temperature": 0.4,
                    "response_mime_type": "application/json",
                }
            )

            text2 = response2.text.strip()
            try:
                data2 = json.loads(text2)
                new_domain = data2.get("domain", domain_text)
                new_problem = data2.get("problem", problem_text)
                explanation = data2.get("explanation", explanation)
            except Exception:
                print("Errore nel parsing della seconda risposta, mantengo i file originali.")
                new_domain, new_problem = domain_text, problem_text

        else:
            print("\nModifiche approvate dall'autore.")

        return new_domain, new_problem

    def run(self):
        print("=== QuestMaster Phase 1: Story Generation ===\n")

        lore_file = None
        for ext in [".docx", ".doc", ".txt", ".md"]:
            candidate = f"lore{ext}"
            if os.path.exists(candidate):
                lore_file = candidate
                break

        lore = ""
        branching = {"min": "N/A", "max": "N/A"}
        depth = {"min": "N/A", "max": "N/A"}

        if lore_file:
            print(f"File di lore trovato: {lore_file}")
            try:
                if lore_file.endswith(".docx"):
                    doc = Document(lore_file)
                    full_text = "\n".join([p.text for p in doc.paragraphs])
                else:
                    with open(lore_file, "r", encoding="utf-8") as f:
                        full_text = f.read()

                def extract_section(label):
                    import re
                    pattern = rf"{label}:(.*?)(?=\n[A-Z][a-zA-Z ]+:|$)"
                    match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
                    return match.group(1).strip() if match else ""

                lore = extract_section("Quest Description") or full_text.strip()
                branching_text = extract_section("Branching Factor")
                depth_text = extract_section("Depth Constraints")

                def parse_range(input_str):
                    if not input_str:
                        return "N/A", "N/A"
                    normalized = re.sub(r"[–—−]", "-", input_str).strip()
                    parts = normalized.split("-")
                    if len(parts) == 2:
                        return parts[0].strip(), parts[1].strip()
                    return "N/A", "N/A"

                branching_min, branching_max = parse_range(branching_text)
                depth_min, depth_max = parse_range(depth_text)
                branching = {"min": branching_min, "max": branching_max}
                depth = {"min": depth_min, "max": depth_max}

                print("Lore caricata correttamente dal documento.")
                print(f"Branching: {branching}, Depth: {depth}\n")

            except Exception as e:
                print(f"Errore durante la lettura del file di lore: {e}")
                lore = input("Inserisci la descrizione della tua storia (Lore):\n> ")
        else:
            print("Nessun file di lore trovato, procedo con input manuale.\n")
            lore = input("Inserisci la descrizione della tua storia (Lore):\n> ")
            branching_input = input("Branching Factor (MIN-MAX, es. 2-3): ")
            depth_input = input("Depth (MIN-MAX, es. 2-3): ")

            def parse_range(input_str):
                if not input_str:
                    return "N/A", "N/A"
                normalized = re.sub(r"[–—−]", "-", input_str).strip()
                parts = normalized.split("-")
                if len(parts) == 2 and all(p.strip().isdigit() for p in parts):
                    return parts[0].strip(), parts[1].strip()
                elif len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
                else:
                    return "N/A", "N/A"

            branching_min, branching_max = parse_range(branching_input)
            depth_min, depth_max = parse_range(depth_input)
            branching = {"min": branching_min, "max": branching_max}
            depth = {"min": depth_min, "max": depth_max}

        domain, problem = self.generate_pddl(lore, branching, depth)
        
        initial_dir = os.path.join(self.output_dir, "initial_attempt")
        os.makedirs(initial_dir, exist_ok=True)
        with open(os.path.join(initial_dir, "domain.pddl"), "w") as f:
            f.write(domain)
        with open(os.path.join(initial_dir, "problem.pddl"), "w") as f:
            f.write(problem)
        print(f"Tentativo iniziale salvato in '{initial_dir}/'")

        valid, message, planner_output = self.validate_pddl(domain, problem)

        attempts = 0
        while not valid and attempts < 5:
            print(f"\n PDDL non valido ({message}). Tentativo di correzione ({attempts + 1}/2)...")
            domain, problem = self.reflection_agent(domain, problem, message, planner_output)
            valid, message, planner_output = self.validate_pddl(domain, problem)
            attempts += 1

        final_dir = self.output_dir 
        os.makedirs(final_dir, exist_ok=True)
        with open(os.path.join(final_dir, "domain.pddl"), "w") as f:
            f.write(domain)
        with open(os.path.join(final_dir, "problem.pddl"), "w") as f:
            f.write(problem)
            
        with open(os.path.join(final_dir, "report.json"), "w") as f:
            json.dump({
                "lore": lore,
                "branching": branching,
                "depth": depth,
                "valid": valid,
                "validation_message": message
            }, f, indent=2)

        print(f"\n Output salvati in '{final_dir}/'")
        print(f"Stato finale: {message}\n")
