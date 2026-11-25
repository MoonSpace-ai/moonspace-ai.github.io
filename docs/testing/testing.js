const testingFilters = document.querySelector('.testing-filters');

if (testingFilters) {
  const buttons = [...testingFilters.querySelectorAll('[data-testing-filter]')];
  const archive = document.querySelector('#testing-archive');
  const noMatches = document.querySelector('#testing-no-matches');
  const status = document.querySelector('#testing-filter-status');
  const cards = [...document.querySelectorAll('[data-testing-tags]')].map(card => ({
    card,
    tags: JSON.parse(card.dataset.testingTags),
    archived: card.closest('#testing-archive') !== null,
  }));

  function filterActivities(selected) {
    const tag = selected.dataset.testingFilter;
    let currentCount = 0;
    let archiveCount = 0;
    for (const {card, tags, archived} of cards) {
      const matches = !tag || tags.includes(tag);
      card.hidden = !matches;
      if (matches) {
        if (archived) archiveCount += 1;
        else currentCount += 1;
      }
    }
    for (const button of buttons) {
      button.setAttribute('aria-pressed', String(button === selected));
    }
    if (archive) archive.hidden = archiveCount === 0;
    if (noMatches) noMatches.hidden = currentCount > 0;
    status.textContent = `${selected.textContent}：${currentCount} 项当前活动，${archiveCount} 项往期活动。`;
  }

  for (const button of buttons) {
    button.addEventListener('click', () => filterActivities(button));
  }
  testingFilters.hidden = false;
}
