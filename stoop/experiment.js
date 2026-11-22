var jsPsych = initJsPsych();
var timeline = [];

var CONGRUENT_REPEATS = 3;       //4 congruent pairs x3 = 12 to match the 12 incongruent pairss    //how many times the full 24-trial list is run
var FIXATION_DURATION_MS = 1000;
var stroop_trial_number = 0;

var welcome = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: "Welcome to the Stroop Task experiment. Press any key to begin."
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
};

var colours = [
  { name: 'RED',    ink: 'red',    key: 'r' },
  { name: 'GREEN',  ink: 'green',  key: 'g' },
  { name: 'BLUE',   ink: 'blue',   key: 'b' },
  { name: 'YELLOW', ink: 'yellow', key: 'y' }
];


var fixation = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: '<div style="font-size:60px;">+</div>',
  choices: "NO_KEYS",
  trial_duration: FIXATION_DURATION_MS,
};

var test_trial = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: '<p class="stroop-word blue">RED</p>',  
  choices: ['r', 'g', 'b', 'y'],                 
  prompt: mapping_legend                         
};

//create congurent trials
var congruent_trials = [];

for (var colour of colours) {
    congruent_trials.push({
        word: colour.name,
        ink: colour.ink,
        condition: 'congruent',
        correct_key: colour.key
    });
}



//congruent_trials = 3 * congruent_trials we can't do this in js
congruent_trials = congruent_trials.flatMap(trial =>
  Array(CONGRUENT_REPEATS).fill(trial)
);

console.log(congruent_trials)
console.log(congruent_trials.length)

var incongruent_trials = [];

for (var word_colour of colours) {
    //to not have duplicate of what we have in congruent trials
  for (var ink_colour of colours) {
    if (word_colour.name !== ink_colour.name) {
      incongruent_trials.push({
        word: word_colour.name,
        ink: ink_colour.ink,
        condition: 'incongruent',
        correct_key: ink_colour.key    
      });
    }
  }
}


console.log(incongruent_trials)
console.log(incongruent_trials.length)

var trial_list = congruent_trials.concat(incongruent_trials);
console.log(trial_list.length);  

var stroop_trial = {
  type: jsPsychHtmlKeyboardResponse,

  stimulus: function() {
    var word = jsPsych.evaluateTimelineVariable('word');
    var ink = jsPsych.evaluateTimelineVariable('ink');

    return `<p class="stroop-word ${ink}">${word}</p>`;
  },

  choices: ['r', 'g', 'b', 'y'],
  prompt: mapping_legend,
  data: {
    task: 'stroop',
    word: jsPsych.timelineVariable('word'),
    ink: jsPsych.timelineVariable('ink'),
    condition: jsPsych.timelineVariable('condition'),
    correct_key: jsPsych.timelineVariable('correct_key')
  },
  on_finish: function(data) {
  //data.correct = data.response === data.correct_key; be careul this doesn't work
  data.correct = jsPsych.pluginAPI.compareKeys(data.response, data.correct_key);
  stroop_trial_number++;
  data.trial_number = stroop_trial_number;
}
};

var stroop_procedure = {
  timeline: [fixation,stroop_trial],
  timeline_variables: trial_list,
  randomize_order: true
};

var results_screen = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: function () {
    
    var stroop_data = jsPsych.data.get().filter({task: 'stroop'});

    var total_trials = stroop_data.count();

    var correct_trials = stroop_data.filter({correct: true}).count();

    var accuracy = (correct_trials / total_trials) * 100;
    return `
      <h2>Experiment complete!</h2>
      <p>You answered ${correct_trials} out of ${total_trials} correctly.</p>
      <p>Your accuracy was ${accuracy.toFixed(1)}%.</p>
      <button id="download-button">Download results (CSV)</button>
    `;
  },
  choices: 'NO_KEYS',
  data: { task: 'results' },
  on_load: function () {
    document.getElementById('download-button').addEventListener('click', function () {
      jsPsych.data.get()
        .filter({ task: 'stroop' })
        .filterColumns([
            'trial_number',
            'word',
            'ink',
            'condition',
            'correct_key',
            'response',
            'correct',
            'rt'
            ])
        .localSave('csv', 'stroop_results.csv');
    });
  }
};




timeline.push(welcome);
timeline.push(instructions);
//timeline.push(test_trial);
timeline.push(stroop_procedure);
timeline.push(results_screen);
jsPsych.run(timeline);

