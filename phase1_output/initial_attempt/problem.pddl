; Define the problem for Sara Walker's quest
(define (problem sara-walker-mission)
    ; Link to the domain definition
    (:domain sara-walker-quest)

    ; Define the objects involved in this specific problem instance
    (:objects
        sara - character
        city lab ruins - location
        alien1 machine1 - enemy
        laser_gun - weapon
        time_machine - device
    )

    ; Define the initial state of the world
    (:init
        ; Sara's initial position and status
        (at sara city) ; Sara starts in the city
        (has-weapon sara laser_gun) ; Sara has a laser gun
        (at-future sara) ; Sara is currently in the future

        ; Enemies present in locations
        (enemy-present alien1 city) ; An alien is in the city, potentially blocking a direct path or requiring a fight
        (enemy-present machine1 ruins) ; A machine is in the ruins, guarding calibration data

        ; Time machine location and status
        (is-time-machine time_machine) ; The time machine is a device
        (at time_machine lab) ; The time machine is initially located in the lab

        ; Resources available at locations
        (has-power-source lab) ; The lab has a power source that Sara can acquire
        (has-calibration-data ruins) ; The ruins contain calibration data that Sara can acquire
    )

    ; Define the goal state to be achieved
    (:goal (and
        (at-past sara) ; Sara must successfully travel to the past
        (world-saved) ; The world must be saved
    ))
)
