const dz = document.getElementById('dz');
const fi = document.getElementById('fi');
const gb = document.getElementById('gb');
const invEl = document.getElementById('invoice_number');
const prevTag = document.getElementById('prev-tag');
const filepill = document.getElementById('filepill');
const pillName = document.getElementById('pill-name');
let sel = null;

/* Invoice preview */
function onNum() {
    const v = invEl.value || '1';
    prevTag.textContent = 'FAC-' + String(v).padStart(3, '0');
}
invEl.addEventListener('input', onNum);

/* Step progress */
function setStep(n) {
    const labels = { 1: 'N° facture', 2: 'Fichier prêt', 3: 'Terminé ✓' };
    document.getElementById('step-lbl').textContent = labels[n] || '';
    [1, 2, 3].forEach(i => {
        const d = document.getElementById('d' + i);
        d.classList.remove('active', 'done');
        if (i < n) d.classList.add('done');
        else if (i === n) d.classList.add('active');
    });
    document.getElementById('tl1').style.width = n >= 2 ? '100%' : '0%';
    document.getElementById('tl2').style.width = n >= 3 ? '100%' : '0%';
}

/* File handling */
fi.onchange = e => { if (e.target.files[0]) attach(e.target.files[0]); };
dz.ondragover = e => { e.preventDefault(); dz.classList.add('over'); };
dz.ondragleave = () => dz.classList.remove('over');
dz.ondrop = e => {
    e.preventDefault(); dz.classList.remove('over');
    if (e.dataTransfer.files[0]) attach(e.dataTransfer.files[0]);
};

function attach(f) {
    sel = f;
    pillName.textContent = f.name;
    filepill.classList.add('show');
    dz.classList.add('filled');
    document.getElementById('dz-body').style.opacity = '0.35';
    gb.disabled = false;
    setStep(2);
    clearStatus();
}

function clearFile() {
    sel = null; fi.value = '';
    filepill.classList.remove('show');
    dz.classList.remove('filled');
    document.getElementById('dz-body').style.opacity = '1';
    gb.disabled = true;
    setStep(1);
    clearStatus();
}

/* Status */
const SVG = {
    spin: `<svg class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>`,
    ok: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    err: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
    doc: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/></svg>`,
};

function showStatus(cls, ico, msg, dlHref, dlName) {
    const el = document.getElementById('st');
    const dlEl = document.getElementById('st-dl');
    el.className = 'statusbar show ' + cls;
    document.getElementById('st-ico').innerHTML = ico;
    document.getElementById('st-msg').textContent = msg;
    dlEl.classList.add('hidden');
    if (dlHref) {
        dlEl.href = dlHref; dlEl.download = dlName;
        dlEl.textContent = '↓ ' + dlName;
        dlEl.classList.remove('hidden');
    }
}

function clearStatus() {
    const el = document.getElementById('st');
    el.className = 'statusbar';
}

/* Generate */
async function go() {
    if (!sel) return;
    gb.disabled = true;
    document.getElementById('btn-lbl').textContent = 'Génération…';
    document.getElementById('btn-ico').innerHTML = SVG.spin;
    showStatus('s-load', SVG.spin, 'Traitement en cours, veuillez patienter…');

    try {
        const fd = new FormData();
        fd.append('file', sel);
        fd.append('invoice_number', invEl.value || '1');
        const r = await fetch('/generate', { method: 'POST', body: fd });
        if (!r.ok) { const e = await r.json(); throw new Error(e.message || 'Erreur serveur'); }
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const disposition = r.headers.get('Content-Disposition');
        let name = 'facture.pdf';
        if (disposition && disposition.includes('filename=')) {
            name = disposition.split('filename=')[1].replace(/"/g, '');
        }
        showStatus('s-ok', SVG.ok, 'Facture générée avec succès.', url, name);
        setStep(3);
    } catch (e) {
        showStatus('s-err', SVG.err, e.message);
    } finally {
        gb.disabled = false;
        document.getElementById('btn-lbl').textContent = 'Générer la facture PDF';
        document.getElementById('btn-ico').innerHTML = SVG.doc;
    }
}