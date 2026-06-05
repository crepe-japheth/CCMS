function initQrScanner(redirectUrlTemplate) {
    const readerElement = document.getElementById('qr-reader');
    if (!readerElement || typeof Html5Qrcode === 'undefined') {
        return;
    }

    const scanner = new Html5Qrcode('qr-reader');
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    const onScanSuccess = (decodedText) => {
        scanner.stop().catch(() => {});
        const tracking = decodedText.trim();
        const url = redirectUrlTemplate.replace('TRACKING_PLACEHOLDER', encodeURIComponent(tracking));
        window.location.href = url;
    };

    Html5Qrcode.getCameras()
        .then((cameras) => {
            if (!cameras || cameras.length === 0) {
                readerElement.innerHTML = '<p class="p-4 text-sm text-slate-500">No camera found. Use manual entry instead.</p>';
                return;
            }
            scanner.start(cameras[0].id, config, onScanSuccess, () => {});
        })
        .catch(() => {
            readerElement.innerHTML = '<p class="p-4 text-sm text-slate-500">Camera unavailable. Use manual entry instead.</p>';
        });
}
