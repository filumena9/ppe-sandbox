import random
import expyriment as xpy

import config

#isi = interstimulus interval


# Experiment initialization
experiment = xpy.design.Experiment(name=config.EXPERIMENT_NAME, background_colour=config.BACKGROUND_COLOUR, foreground_colour=config.FOREGROUND_COLOUR)
experiment.data_variable_names = ["condition", "trial", "isi_ms", "frame_ms", "response", "group_response", "key", "rt_ms"]
xpy.control.initialize(experiment)

#helper function for building blocks
def create_block(condition):
    """Build one shuffled block: every ISI in config.ISI_VALUES_MS, TRIALS_PER_ISI times each."""
    block = xpy.design.Block(name=condition)
    block.set_factor("condition", condition)
    block.add_trials_full_factorial({"isi_ms": config.ISI_VALUES_MS},
                                    copies=config.TRIALS_PER_ISI)
    block.shuffle_trials()
    return block



# DOTS stimuli
dots_first_image = xpy.stimuli.Canvas(size=config.IMAGE_SIZE, colour=config.BACKGROUND_COLOUR)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_first_image)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_CENTER_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_first_image)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_CENTER_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_first_image)

dots_second_image = xpy.stimuli.Canvas(size=config.IMAGE_SIZE, colour=config.BACKGROUND_COLOUR)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_CENTER_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_second_image)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_CENTER_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_second_image)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(dots_second_image)

# SHAPES stimuli
shapes_first_image = xpy.stimuli.Canvas(size=config.IMAGE_SIZE, colour=config.BACKGROUND_COLOUR)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_first_image)
xpy.stimuli.Shape(vertex_list=xpy.misc.geometry.vertices_regular_polygon(3, config.TRIANGLE_RADIUS), position=(config.X_CENTER_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_first_image)
xpy.stimuli.Rectangle(size=config.SQUARE_SIZE, position=(config.X_CENTER_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_first_image)

shapes_second_image = xpy.stimuli.Canvas(size=config.IMAGE_SIZE, colour=config.BACKGROUND_COLOUR)
xpy.stimuli.Shape(vertex_list=xpy.misc.geometry.vertices_regular_polygon(3, config.TRIANGLE_RADIUS), position=(config.X_CENTER_LEFT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_second_image)
xpy.stimuli.Rectangle(size=config.SQUARE_SIZE, position=(config.X_CENTER_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_second_image)
xpy.stimuli.Circle(radius=config.DOT_RADIUS, position=(config.X_RIGHT, config.Y_ITEMS), colour=config.FOREGROUND_COLOUR).plot(shapes_second_image)

# Fixation cross and text screens
fixation_cross = xpy.stimuli.FixCross(size=config.FIXATION_SIZE, line_width=config.FIXATION_LINE_WIDTH, colour=config.FOREGROUND_COLOUR)
fixation_screen = xpy.stimuli.BlankScreen(colour=config.BACKGROUND_COLOUR)
fixation_cross.plot(fixation_screen)
instructions_screen = xpy.stimuli.TextScreen(heading="Ternus experiment", text="Keep your eyes on the central cross.\n\nLEFT = element motion\nRIGHT = group motion\n\nPress SPACE to start.")
response_prompt_screen = xpy.stimuli.TextScreen(heading="What did you see?", text="LEFT = element motion\nRIGHT = group motion")
blank_screen = xpy.stimuli.BlankScreen(colour=config.BACKGROUND_COLOUR)

# Fixation on stimulus and text screens
fixation_cross.plot(dots_first_image)
fixation_cross.plot(dots_second_image)
fixation_cross.plot(shapes_first_image)
fixation_cross.plot(shapes_second_image)
fixation_cross.plot(instructions_screen)
fixation_cross.plot(response_prompt_screen)

# Preloading
dots_first_image.preload()
dots_second_image.preload()
shapes_first_image.preload()
shapes_second_image.preload()
fixation_screen.preload()
instructions_screen.preload()
response_prompt_screen.preload()
blank_screen.preload()

# DOTS block and trial construction
dots_block = create_block("DOTS")
# Randomization of DOTS trials
dots_block.shuffle_trials()
# SHAPES block and trial construction
shapes_block = create_block("SHAPES")

# Randomization of SHAPES trials, can be done with the built in shuffle fucntipn
shapes_block.shuffle_trials()

# Stimuli for DOTS trials
for trial in dots_block.trials:
    trial.add_stimulus(dots_first_image)
    trial.add_stimulus(dots_second_image)
    trial.add_stimulus(fixation_screen)
    trial.add_stimulus(response_prompt_screen)
    trial.add_stimulus(fixation_screen)
    trial.add_stimulus(blank_screen)

# Stimuli for SHAPES trials
for trial in shapes_block.trials:
    trial.add_stimulus(shapes_first_image)
    trial.add_stimulus(shapes_second_image)
    trial.add_stimulus(fixation_screen)
    trial.add_stimulus(response_prompt_screen)
    trial.add_stimulus(fixation_screen)
    trial.add_stimulus(blank_screen)

# Experiment start
experiment.add_block(dots_block)
experiment.add_block(shapes_block)
xpy.control.start(skip_ready_screen=True)

# Counterbalancing
if experiment.subject % 2 == 0:
    experiment.blocks.reverse()

# Instructions
instructions_screen.present()
experiment.keyboard.wait(keys=[xpy.misc.constants.K_SPACE])

# Trial presentation
for block in experiment.blocks:
    for trial in block.trials:
        isi_ms = trial.get_factor("isi_ms")
        trial.stimuli[2].present()
        experiment.clock.wait(config.FIXATION_BEFORE_TRIAL_MS)

        for repetition in range(config.N_IMAGE_PAIRS):
            trial.stimuli[0].present()
            experiment.clock.wait(config.IMAGE_DURATION_MS)
            if isi_ms > 0:
                trial.stimuli[4].present()
                experiment.clock.wait(isi_ms)

            trial.stimuli[1].present()
            experiment.clock.wait(config.IMAGE_DURATION_MS)
            if isi_ms > 0:
                trial.stimuli[4].present()
                experiment.clock.wait(isi_ms)

        # Response collection
        trial.stimuli[3].present()
        key, rt_ms = experiment.keyboard.wait(keys=[xpy.misc.constants.K_LEFT, xpy.misc.constants.K_RIGHT])

        if key == xpy.misc.constants.K_LEFT:
            response_label = "element"
            group_response = 0
        else:
            response_label = "group"
            group_response = 1

        # Intertrial interval
        trial.stimuli[5].present()
        experiment.clock.wait(config.INTERTRIAL_INTERVAL_MS)
        # Data saving
        experiment.data.add([block.get_factor("condition"), trial.id, isi_ms, config.IMAGE_DURATION_MS, response_label, group_response, key, rt_ms])
        experiment.data.save()

# Experiment end
xpy.control.end()