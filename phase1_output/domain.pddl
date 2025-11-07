; Define the domain for Sara Walker's adventure
(define (domain sara-walker-quest)
    ; Define the types of objects in this domain
    (:types
        character location enemy weapon device - object
    )

    ; Define the predicates (facts) that can be true or false
    (:predicates
        (at ?c - character ?l - location) ; Character ?c is at location ?l
        (has-weapon ?c - character ?w - weapon) ; Character ?c has weapon ?w
        (weapon-charged ?w - weapon) ; Weapon ?w is charged
        (enemy-present ?e - enemy ?l - location) ; Enemy ?e is present at location ?l
        (enemy-defeated ?e - enemy) ; Enemy ?e has been defeated
        (is-time-machine ?d - device) ; Device ?d is a time machine
        (time-machine-located ?c - character ?d - device) ; Character ?c has located time machine ?d
        (time-machine-powered ?d - device) ; Time machine ?d is powered
        (time-machine-calibrated ?d - device) ; Time machine ?d is calibrated
        (has-power-source ?l - location) ; Location ?l contains a power source that can be acquired
        (has-calibration-data ?l - location) ; Location ?l contains calibration data that can be acquired
        (has-acquired-power-source ?c - character) ; Character ?c has acquired a power source
        (has-acquired-calibration-data ?c - character) ; Character ?c has acquired calibration data
        (at-future ?c - character) ; Character ?c is in the future
        (at-past ?c - character) ; Character ?c is in the past
        (world-saved) ; The world has been saved
    )

    ; Define the actions Sara can perform

    ; Action: Move from one location to another
    (:action move
        :parameters (?c - character ?from ?to - location)
        :precondition (and
            (at ?c ?from) ; Character must be at the starting location
        )
        :effect (and
            (not (at ?c ?from)) ; Character is no longer at the starting location
            (at ?c ?to) ; Character is now at the destination location
        )
    )

    ; Action: Charge a weapon at a location
    (:action charge-weapon
        :parameters (?c - character ?w - weapon ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the location
            (has-weapon ?c ?w) ; Character must have the weapon
            (not (weapon-charged ?w)) ; Weapon must not already be charged
        )
        :effect (and
            (weapon-charged ?w) ; Weapon becomes charged
        )
    )

    ; Action: Fight an enemy at a location
    (:action fight-enemy
        :parameters (?c - character ?e - enemy ?w - weapon ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the location
            (enemy-present ?e ?l) ; Enemy must be present at the location
            (has-weapon ?c ?w) ; Character must have a weapon
            (weapon-charged ?w) ; Weapon must be charged to fight
        )
        :effect (and
            (not (enemy-present ?e ?l)) ; Enemy is no longer present
            (enemy-defeated ?e) ; Enemy is defeated
            (not (weapon-charged ?w)) ; Weapon loses its charge after use
        )
    )

    ; Action: Locate the time machine
    (:action locate-time-machine
        :parameters (?c - character ?m - device ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the location where the time machine is
            (is-time-machine ?m) ; The device must be a time machine
            (not (time-machine-located ?c ?m)) ; Time machine must not already be located by this character
        )
        :effect (and
            (time-machine-located ?c ?m) ; Time machine is now located
        )
    )

    ; Action: Acquire a power source from a location
    (:action acquire-power-source
        :parameters (?c - character ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the location
            (has-power-source ?l) ; The location must have a power source
            (not (has-acquired-power-source ?c)) ; Character must not already have a power source
        )
        :effect (and
            (has-acquired-power-source ?c) ; Character acquires the power source
            (not (has-power-source ?l)) ; The power source is consumed/removed from the location
        )
    )

    ; Action: Acquire calibration data from a location
    (:action acquire-calibration-data
        :parameters (?c - character ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the location
            (has-calibration-data ?l) ; The location must have calibration data
            (not (has-acquired-calibration-data ?c)) ; Character must not already have calibration data
        )
        :effect (and
            (has-acquired-calibration-data ?c) ; Character acquires the calibration data
            (not (has-calibration-data ?l)) ; The calibration data is consumed/removed from the location
        )
    )

    ; Action: Power the time machine using an acquired power source
    (:action power-time-machine
        :parameters (?c - character ?m - device ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the time machine's location
            (time-machine-located ?c ?m) ; Time machine must be located
            (has-acquired-power-source ?c) ; Character must have an acquired power source
            (not (time-machine-powered ?m)) ; Time machine must not already be powered
        )
        :effect (and
            (time-machine-powered ?m) ; Time machine becomes powered
            (not (has-acquired-power-source ?c)) ; Acquired power source is used up
        )
    )

    ; Action: Calibrate the time machine using acquired calibration data
    (:action calibrate-time-machine
        :parameters (?c - character ?m - device ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the time machine's location
            (time-machine-located ?c ?m) ; Time machine must be located
            (has-acquired-calibration-data ?c) ; Character must have acquired calibration data
            (not (time-machine-calibrated ?m)) ; Time machine must not already be calibrated
        )
        :effect (and
            (time-machine-calibrated ?m) ; Time machine becomes calibrated
            (not (has-acquired-calibration-data ?c)) ; Acquired calibration data is used up
        )
    )

    ; Action: Travel to the past using the time machine
    (:action travel-to-past
        :parameters (?c - character ?m - device ?l - location)
        :precondition (and
            (at ?c ?l) ; Character must be at the time machine's location
            (time-machine-located ?c ?m) ; Time machine must be located
            (time-machine-powered ?m) ; Time machine must be powered
            (time-machine-calibrated ?m) ; Time machine must be calibrated
            (at-future ?c) ; Character must currently be in the future
        )
        :effect (and
            (not (at-future ?c)) ; Character is no longer in the future
            (at-past ?c) ; Character is now in the past
            (world-saved) ; The world is saved
        )
    )
)
