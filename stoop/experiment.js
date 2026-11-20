var jsPsych = initJsPsych();
var timeline = [];

var welcome = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "Welcome to the Stoop Task experiment. Press any key to begin."
};

var mapping_legend_instructions = `
  <div class="instruction-mapping">
    <span class="red">RED</span> = R &nbsp;
    <span class="green">GREEN</span> = G &nbsp;
    <span class="blue">BLUE</span> = B &nbsp;
    <span class="yellow">YELLOW</span> = Y
  </div>
`;

var mapping_legend = `
  <div class="legend">
    <div><kbd>R</kbd> red</div>
    <div><kbd>G</kbd> green</div>
    <div><kbd>B</kbd> blue</div>
    <div><kbd>Y</kbd> yellow</div>
  </div>
`;

var instructions = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
    <h2>Stroop Task</h2>
    <p>In this experiment, you will see color names (red, green, blue, yellow) one at a time.</p>
    <p>Each word is printed in a coloured ink. Respond to the <strong>ink colour</strong>,
    not to what the word says.</p>
    <p>For example, if you see <span class="blue">RED</span>, the ink is blue, so press <kbd>B</kbd>.</p>
    ${mapping_legend_instructions}
    <p>Respond as quickly and as accurately as you can.</p>
    <p>Press any key to begin.</p>
  `,
  post_trial_gap: 2000
};

var test_trial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: '<p class="stimulus blue">RED</p>',  
  choices: ['r', 'g', 'b', 'y'],                 
  prompt: mapping_legend                         
};

timeline.push(welcome);
timeline.push(instructions);
timeline.push(test_trial);
jsPsych.run(timeline);


