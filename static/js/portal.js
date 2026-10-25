document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('[data-invest-calculator]');
    if (!form) return;

    const acreage = form.querySelector('#parcel-acres');
    const use = form.querySelector('#development-use');
    const acresOutput = form.querySelector('#acres-output');
    const landBasis = form.querySelector('#land-basis');
    const yearFiveValue = form.querySelector('#year-five-value');
    const appreciationUplift = form.querySelector('#appreciation-uplift');
    const annualIncome = form.querySelector('#annual-income');
    const yieldLabel = form.querySelector('#yield-label');
    const useSummary = form.querySelector('#use-summary');
    const currency = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0,
    });

    const updateScenario = () => {
        const acres = Number(acreage.value);
        const selectedUse = use.selectedOptions[0];
        const pricePerAcre = Number(form.dataset.landPrice);
        const annualAppreciation = Number(form.dataset.appreciation) / 100;
        const grossYield = Number(selectedUse.dataset.yield) / 100;
        const acquisitionBasis = acres * pricePerAcre;
        const yearFiveEstimate = acquisitionBasis * ((1 + annualAppreciation) ** 5);

        const acreageLabel = acres === 10 ? '10+' : String(acres);
        acresOutput.value = acreageLabel;
        acresOutput.textContent = acreageLabel;
        landBasis.textContent = currency.format(acquisitionBasis);
        yearFiveValue.textContent = currency.format(yearFiveEstimate);
        appreciationUplift.textContent = currency.format(yearFiveEstimate - acquisitionBasis);
        annualIncome.textContent = currency.format(acquisitionBasis * grossYield);
        yieldLabel.textContent = `${(grossYield * 100).toFixed(0)}% illustrative gross yield`;
        useSummary.textContent = selectedUse.dataset.summary;
    };

    acreage.addEventListener('input', updateScenario);
    use.addEventListener('change', updateScenario);
    updateScenario();
});
