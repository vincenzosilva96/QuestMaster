from questmaster_phase1 import QuestMasterPhase1
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY") 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fast_downward_path = os.path.join(base_dir, "fast-downward-24.06.1", "fast-downward.py")
    qm = QuestMasterPhase1(
        gemini_api_key=gemini_api_key,
        fast_downward_path=fast_downward_path
        #fast_downward_path="*/fast-downward-24.06.1/fast-downward.py"
        
    )
    qm.run()
