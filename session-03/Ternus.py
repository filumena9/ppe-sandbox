import random
import expyriment as xpy

# Experiment initialization
experiment = xpy.design.Experiment(name="Ternus experiment", background_colour=(0, 0, 0), foreground_colour=(255, 255, 255))
experiment.data_variable_names = ["condition", "trial", "isi_ms", "frame_ms", "response", "group_response", "key", "rt_ms"]
xpy.control.initialize(experiment)

# DOTS stimuli
list1 = []
dots_first_image = xpy.stimuli.Canvas(size=(600, 300), colour=(0, 0, 0))
xpy.stimuli.Circle(radius=20, position=(-120, -50), colour=(255, 255, 255)).plot(dots_first_image)
xpy.stimuli.Circle(radius=20, position=(-40, -50), colour=(255, 255, 255)).plot(dots_first_image)
xpy.stimuli.Circle(radius=20, position=(40, -50), colour=(255, 255, 255)).plot(dots_first_image)

dots_second_image = xpy.stimuli.Canvas(size=(600, 300), colour=(0, 0, 0))
xpy.stimuli.Circle(radius=20, position=(-40, -50), colour=(255, 255, 255)).plot(dots_second_image)
xpy.stimuli.Circle(radius=20, position=(40, -50), colour=(255, 255, 255)).plot(dots_second_image)
xpy.stimuli.Circle(radius=20, position=(120, -50), colour=(255, 255, 255)).plot(dots_second_image)

# SHAPES stimuli
shapes_first_image = xpy.stimuli.Canvas(size=(600, 300), colour=(0, 0, 0))
xpy.stimuli.Circle(radius=20, position=(-120, -50), colour=(255, 255, 255)).plot(shapes_first_image)
xpy.stimuli.Shape(vertex_list=xpy.misc.geometry.vertices_regular_polygon(3, 54), position=(-40, -50), colour=(255, 255, 255)).plot(shapes_first_image)
xpy.stimuli.Rectangle(size=(35, 35), position=(40, -50), colour=(255, 255, 255)).plot(shapes_first_image)

shapes_second_image = xpy.stimuli.Canvas(size=(600, 300), colour=(0, 0, 0))
xpy.stimuli.Shape(vertex_list=xpy.misc.geometry.vertices_regular_polygon(3, 54), position=(-40, -50), colour=(255, 255, 255)).plot(shapes_second_image)
xpy.stimuli.Rectangle(size=(35, 35), position=(40, -50), colour=(255, 255, 255)).plot(shapes_second_image)
xpy.stimuli.Circle(radius=20, position=(120, -50), colour=(255, 255, 255)).plot(shapes_second_image)

# Fixation cross and text screens
fixation_cross = xpy.stimuli.FixCross(size=(20, 20), line_width=4, colour=(255, 255, 255))
fixation_screen = xpy.stimuli.BlankScreen(colour=(0, 0, 0))
fixation_cross.plot(fixation_screen)
instructions_screen = xpy.stimuli.TextScreen(heading="Ternus experiment", text="Keep your eyes on the central cross.\n\nLEFT = element motion\nRIGHT = group motion\n\nPress SPACE to start.")
response_prompt_screen = xpy.stimuli.TextScreen(heading="What did you see?", text="LEFT = element motion\nRIGHT = group motion")
blank_screen = xpy.stimuli.BlankScreen(colour=(0, 0, 0))

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
dots_block = xpy.design.Block(name="DOTS")
dots_block.set_factor("condition", "DOTS")
for isi_ms in [0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 1000, 1000, 1000, 1000, 1000]:
    trial = xpy.design.Trial()
    trial.set_factor("isi_ms", isi_ms)
    dots_block.add_trial(trial)

# Randomization of DOTS trials
for index in range(len(dots_block.trials) - 1, 0, -1):
    swap_index = random.randint(0, index)
    dots_block.trials[index], dots_block.trials[swap_index] = dots_block.trials[swap_index], dots_block.trials[index]

# SHAPES block and trial construction
shapes_block = xpy.design.Block(name="SHAPES")
shapes_block.set_factor("condition", "SHAPES")
for isi_ms in [0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 500, 500, 500, 500, 500, 1000, 1000, 1000, 1000, 1000]:
    trial = xpy.design.Trial()
    trial.set_factor("isi_ms", isi_ms)
    shapes_block.add_trial(trial)

# Randomization of SHAPES trials
for index in range(len(shapes_block.trials) - 1, 0, -1):
    swap_index = random.randint(0, index)
    shapes_block.trials[index], shapes_block.trials[swap_index] = shapes_block.trials[swap_index], shapes_block.trials[index]

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
        experiment.clock.wait(200)

        for repetition in range(3):
            trial.stimuli[0].present()
            experiment.clock.wait(250)
            if isi_ms > 0:
                trial.stimuli[4].present()
                experiment.clock.wait(isi_ms)

            trial.stimuli[1].present()
            experiment.clock.wait(250)
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
        experiment.clock.wait(500)
        # Data saving
        experiment.data.add([block.get_factor("condition"), trial.id, isi_ms, 250, response_label, group_response, key, rt_ms])
        experiment.data.save()

# Experiment end
xpy.control.end()