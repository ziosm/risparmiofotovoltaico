// Calcolatore Risparmio
function calcolaRisparmio() {
    const bollettaMensile = parseFloat(document.getElementById('bolletta').value);

    if (!bollettaMensile || bollettaMensile < 30 || bollettaMensile > 1000) {
        alert('Inserisci un importo valido tra 30€ e 1000€');
        return;
    }

    // Calcoli (formule semplificate ma realistiche)
    const bollettaAnnua = bollettaMensile * 12;
    const consumoAnnuoKwh = bollettaAnnua / 0.25; // €0.25 per kWh medio
    const potenzaImpiantoKw = consumoAnnuoKwh / 1200; // 1200 kWh per kW/anno

    // Risparmio (70% della bolletta coperto da fotovoltaico)
    const risparmioAnnuo = bollettaAnnua * 0.70;
    const risparmio25Anni = risparmioAnnuo * 25;

    // Costo impianto (circa €1400-€1600 per kW)
    const costoImpiantoKw = 1500;
    const costoImpianto = potenzaImpiantoKw * costoImpiantoKw;

    // ROI (con detrazioni 50%)
    const costoEffettivo = costoImpianto * 0.5; // Detrazione 50%
    const roiAnni = Math.round((costoEffettivo / risparmioAnnuo) * 10) / 10;

    // Mostra risultati
    document.getElementById('risparmioAnno').textContent = '€ ' + Math.round(risparmioAnnuo).toLocaleString('it-IT');
    document.getElementById('risparmio25Anni').textContent = '€ ' + Math.round(risparmio25Anni).toLocaleString('it-IT');
    document.getElementById('costoImpianto').textContent = '€ ' + Math.round(costoImpianto).toLocaleString('it-IT');
    document.getElementById('roi').textContent = roiAnni + ' anni';

    // Mostra sezione risultato
    document.getElementById('risultato').style.display = 'block';

    // Scroll al form dopo 2 secondi
    setTimeout(() => {
        document.getElementById('preventivo-fotovoltaico').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 3000);

    // Pre-compila il consumo nel form
    document.getElementById('note').value = `Bolletta mensile: €${bollettaMensile} - Consumo annuo stimato: ${Math.round(consumoAnnuoKwh)} kWh`;
}

// Invio Form
async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('leadForm');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');

    // Disabilita bottone e mostra loader
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    form.querySelector('button[type="submit"]').disabled = true;

    // Raccogli dati
    const formData = {
        nome: document.getElementById('nome').value,
        cognome: document.getElementById('cognome').value || '',
        email: document.getElementById('email').value,
        telefono: document.getElementById('telefono').value,
        citta: document.getElementById('citta').value,
        provincia: document.getElementById('provincia').value.toUpperCase() || '',
        tipo_immobile: document.getElementById('tipo_immobile').value,
        tempistica: document.getElementById('tempistica').value,
        interesse_batterie: document.getElementById('interesse_batterie').checked,
        interesse_pompa_calore: document.getElementById('interesse_pompa_calore').checked,
        marketing_consent: document.getElementById('marketing_consent').checked,
        note: document.getElementById('note').value,
        consumo_mensile: parseFloat(document.getElementById('bolletta').value) || null,
        source: 'landing_page',
        utm_source: getUrlParameter('utm_source') || 'organic',
        utm_campaign: getUrlParameter('utm_campaign') || null
    };

    // Calcola dati aggiuntivi se disponibile bolletta
    if (formData.consumo_mensile) {
        const bollettaAnnua = formData.consumo_mensile * 12;
        formData.consumo_annuo_kwh = bollettaAnnua / 0.25;
        formData.risparmio_stimato = bollettaAnnua * 0.70;
        formData.costo_impianto_stimato = (formData.consumo_annuo_kwh / 1200) * 1500;
        formData.roi_anni = ((formData.costo_impianto_stimato * 0.5) / formData.risparmio_stimato).toFixed(1);
    }

    try {
        // Invia al backend
        const response = await fetch('/api/richiesta-preventivo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            // Redirect a thank you page
            window.location.href = '/grazie.html?id=' + result.id;
        } else {
            throw new Error(result.error || 'Errore durante l\'invio');
        }

    } catch (error) {
        console.error('Errore:', error);
        alert('Si è verificato un errore. Riprova tra poco o contattaci direttamente al 333 1234567');

        // Ripristina bottone
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        form.querySelector('button[type="submit"]').disabled = false;
    }
}

// Utility: ottieni parametro URL
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Validazione telefono italiana
document.getElementById('telefono')?.addEventListener('blur', function() {
    const telefono = this.value.replace(/[\s\-]/g, '');
    const isValid = /^(\+39)?[0-9]{9,10}$/.test(telefono);

    if (telefono && !isValid) {
        this.setCustomValidity('Inserisci un numero di telefono italiano valido');
    } else {
        this.setCustomValidity('');
    }
});

// Validazione provincia (2 lettere)
document.getElementById('provincia')?.addEventListener('blur', function() {
    this.value = this.value.toUpperCase();
});

// Auto-scroll quando compila bolletta
document.getElementById('bolletta')?.addEventListener('input', function() {
    if (this.value >= 30) {
        document.querySelector('.btn-primary').style.animation = 'pulse 1s infinite';
    }
});

