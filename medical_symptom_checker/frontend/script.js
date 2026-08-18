const symptomList = [
  'fever',
  'cough',
  'headache',
  'sore_throat',
  'runny_nose',
  'stuffy_nose',
  'sneezing',
  'fatigue',
  'body_aches',
  'chills',
  'nausea',
  'vomiting',
  'diarrhea',
  'abdominal_pain',
  'dizziness',
  'chest_pain',
  'shortness_of_breath',
  'loss_of_appetite',
  'muscle_pain',
  'weakness'
];

const popularSymptoms = ['fever', 'cough', 'headache', 'fatigue', 'body_aches'];

const state = {
  selectedSymptoms: new Set(),
  query: ''
};

const symptomOptionsEl = document.getElementById('symptom-options');
const selectedSymptomsEl = document.getElementById('selected-symptoms');
const popularSymptomsEl = document.getElementById('popular-symptoms');
const resultCountEl = document.getElementById('result-count');
const analyzeBtn = document.getElementById('analyze-btn');
const resetBtn = document.getElementById('reset-btn');
const searchInput = document.getElementById('symptom-search');
const resultsPanel = document.getElementById('results-panel');
const conditionNameEl = document.getElementById('condition-name');
const matchIndicatorEl = document.getElementById('match-indicator');
const reasoningTextEl = document.getElementById('reasoning-text');
const otherResultsEl = document.getElementById('other-results');

function titleCase(value) {
  return value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function renderPopularSymptoms() {
  popularSymptomsEl.innerHTML = '';

  popularSymptoms.forEach((symptom) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'quick-btn';
    button.textContent = titleCase(symptom);
    button.addEventListener('click', () => toggleSymptom(symptom));
    popularSymptomsEl.appendChild(button);
  });
}

function getVisibleSymptoms() {
  const query = state.query.trim().toLowerCase();
  return symptomList.filter((symptom) => {
    const label = titleCase(symptom).toLowerCase();
    return label.includes(query) || symptom.toLowerCase().includes(query);
  });
}

function renderSymptomOptions() {
  const visible = getVisibleSymptoms();
  symptomOptionsEl.innerHTML = '';

  if (visible.length === 0) {
    symptomOptionsEl.innerHTML = '<p style="color: #5f7386; margin: 0;">No matching symptoms found.</p>';
    return;
  }

  visible.forEach((symptom) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `symptom-pill ${state.selectedSymptoms.has(symptom) ? 'selected' : ''}`;
    button.textContent = titleCase(symptom);
    button.setAttribute('aria-pressed', String(state.selectedSymptoms.has(symptom)));
    button.addEventListener('click', () => toggleSymptom(symptom));
    symptomOptionsEl.appendChild(button);
  });
}

function renderSelectedSymptoms() {
  const selected = [...state.selectedSymptoms];

  selectedSymptomsEl.innerHTML = '';
  if (selected.length === 0) {
    selectedSymptomsEl.textContent = 'No symptoms selected yet.';
    selectedSymptomsEl.classList.add('empty-state');
    resultCountEl.textContent = '0 selected';
    return;
  }

  selectedSymptomsEl.classList.remove('empty-state');
  resultCountEl.textContent = `${selected.length} selected`;

  selected.forEach((symptom) => {
    const chip = document.createElement('div');
    chip.className = 'selected-pill';

    const label = document.createElement('span');
    label.textContent = titleCase(symptom);

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.textContent = '×';
    removeBtn.className = 'remove-btn';
    removeBtn.setAttribute('aria-label', `Remove ${titleCase(symptom)}`);
    removeBtn.addEventListener('click', () => toggleSymptom(symptom));

    chip.append(label, removeBtn);
    selectedSymptomsEl.appendChild(chip);
  });
}

function toggleSymptom(symptom) {
  if (state.selectedSymptoms.has(symptom)) {
    state.selectedSymptoms.delete(symptom);
  } else {
    state.selectedSymptoms.add(symptom);
  }

  renderSymptomOptions();
  renderSelectedSymptoms();
}

function resetState() {
  state.selectedSymptoms.clear();
  state.query = '';
  searchInput.value = '';
  resultsPanel.classList.add('hidden');
  conditionNameEl.textContent = '—';
  matchIndicatorEl.textContent = 'Rule Match: 0 / 0 symptoms';
  reasoningTextEl.textContent = 'No analysis yet.';
  otherResultsEl.innerHTML = '';
  renderSymptomOptions();
  renderSelectedSymptoms();
}

async function analyzeSymptoms() {
  const selected = [...state.selectedSymptoms];
  if (selected.length === 0) {
    reasoningTextEl.textContent = 'Please choose at least one symptom before analyzing.';
    resultsPanel.classList.remove('hidden');
    conditionNameEl.textContent = 'No condition selected';
    matchIndicatorEl.textContent = 'Rule Match: 0 / 0 symptoms';
    otherResultsEl.innerHTML = '';
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Checking...';
  resultsPanel.classList.remove('hidden');
  conditionNameEl.textContent = 'Analyzing...';
  matchIndicatorEl.textContent = 'Rule Match: processing';
  reasoningTextEl.textContent = 'Evaluating selected symptoms with the rule engine...';
  otherResultsEl.innerHTML = '';

  try {
    const response = await fetch('http://127.0.0.1:5000/check-symptoms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms: selected })
    });

    if (!response.ok) {
      throw new Error('Unable to analyze symptoms at the moment.');
    }

    const data = await response.json();
    const conditions = data.possible_conditions || [];

    if (!conditions.length) {
      conditionNameEl.textContent = 'No strong rule match';
      matchIndicatorEl.textContent = 'Rule Match: insufficient data';
      reasoningTextEl.textContent = data.reasoning || 'No strong rule match was found. Please select additional symptoms.';
      otherResultsEl.innerHTML = '';
      return;
    }

    const topResult = conditions[0];
    conditionNameEl.textContent = topResult.condition;
    matchIndicatorEl.textContent = `Rule Match: ${topResult.matched_count} / ${topResult.total_required} symptoms`;
    reasoningTextEl.textContent = topResult.explanation;

    otherResultsEl.innerHTML = conditions
      .slice(1)
      .map((item) => `
        <div class="other-card">
          <strong>${item.condition}</strong>
          <span>${item.matched_count}/${item.total_required} symptoms matched</span>
        </div>
      `)
      .join('');
  } catch (error) {
    conditionNameEl.textContent = 'Analysis unavailable';
    matchIndicatorEl.textContent = 'Rule Match: error';
    reasoningTextEl.textContent = 'The service is currently unavailable. Please try again in a moment.';
    otherResultsEl.innerHTML = '';
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze Symptoms';
  }
}

searchInput.addEventListener('input', (event) => {
  state.query = event.target.value;
  renderSymptomOptions();
});

analyzeBtn.addEventListener('click', analyzeSymptoms);
resetBtn.addEventListener('click', resetState);

renderPopularSymptoms();
renderSymptomOptions();
renderSelectedSymptoms();
