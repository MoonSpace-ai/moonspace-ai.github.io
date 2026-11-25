const copyPrompt = document.querySelector('#learn-copy-button');
if (copyPrompt) {
  copyPrompt.addEventListener('click', async () => {
    const prompt = document.querySelector('#learn-prompt');
    const status = document.querySelector('#learn-copy');
    try {
      await navigator.clipboard.writeText(prompt.textContent);
      status.textContent = '已复制提示词。';
    } catch {
      status.textContent = '请选中上方提示词手动复制。';
    }
  });
}

const registrations = document.querySelectorAll('[data-registration-deadline]');
if (registrations.length) {
  const today = new Intl.DateTimeFormat('sv-SE', {timeZone: 'Asia/Shanghai'}).format(new Date());
  for (const registration of registrations) {
    const closed = today > registration.dataset.registrationDeadline;
    registration.firstElementChild.hidden = closed;
    registration.lastElementChild.hidden = !closed;
  }
}

const quiz = document.querySelector('#learn-quiz');
if (quiz) {
  const questions = [...quiz.querySelectorAll('fieldset')];
  const progress = quiz.querySelector('#learn-progress');
  const result = quiz.querySelector('#learn-result');
  const submit = quiz.querySelector('[type="submit"]');
  const reset = quiz.querySelector('[type="reset"]');
  const selected = question => question.querySelector('input:checked');
  const updateProgress = () => {
    const count = questions.filter(selected).length;
    progress.textContent = `已答 ${count} / ${questions.length} 题`;
  };

  quiz.querySelector('.learn-quiz-actions').hidden = false;
  quiz.addEventListener('change', updateProgress);
  quiz.addEventListener('submit', event => {
    event.preventDefault();
    if (!quiz.reportValidity() || questions.some(question => !selected(question))) return;
    let score = 0;
    for (const question of questions) {
      const correct = selected(question).value === question.dataset.answer;
      score += Number(correct);
      const explanation = question.querySelector('.learn-explanation');
      explanation.querySelector('strong').textContent = correct ? '答对了' : '这题可以再想一想';
      explanation.hidden = false;
      question.disabled = true;
    }
    result.textContent = `答对 ${score} / ${questions.length} 题。下方是逐题解析。`;
    result.hidden = false;
    submit.hidden = true;
    reset.hidden = false;
    result.focus();
  });
  quiz.addEventListener('reset', () => {
    for (const question of questions) {
      question.disabled = false;
      question.querySelector('.learn-explanation').hidden = true;
    }
    result.hidden = true;
    reset.hidden = true;
    submit.hidden = false;
    requestAnimationFrame(() => {
      updateProgress();
      questions[0].querySelector('input').focus();
    });
  });
  updateProgress();
}
