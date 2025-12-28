// Глобальный обработчик ошибок
window.addEventListener('error', (e) => {
    console.error('JS Error:', e.message, e.filename, e.lineno);
});

// Функция для обновления предпросмотра текста на изображении
function updateTextPreview() {
    const textOverlay = document.getElementById('text-overlay');
    textOverlay.innerHTML = '';

    document.querySelectorAll('#textBlocks .block-item').forEach(block => {
        const text = block.querySelector('.text-block-input').value;
        const fontSize = block.querySelector('.text-block-font-size').value;
        const color = block.querySelector('.text-block-color').value;
        const strokeColor = block.querySelector('.text-block-stroke-color').value;
        const span = document.createElement('span');
        span.style.position = 'absolute';
        span.style.left = '50%';
        span.style.top = '50%';
        span.style.transform = 'translate(-50%, -50%)';
        span.style.color = color;
        span.style.textShadow = `0 0 2px ${strokeColor}`;
        span.style.fontSize = `${fontSize}px`;
        span.style.fontFamily = 'Arial, sans-serif';
        span.style.whiteSpace = 'nowrap';
        span.textContent = text;

        textOverlay.appendChild(span);
    });
}

// Вызываем обновление предпросмотра при изменении полей
document.addEventListener('input', (e) => {
    if (e.target.classList.contains('text-block-input') ||
        e.target.classList.contains('text-block-font-size') ||
        e.target.classList.contains('text-block-color') ||
        e.target.classList.contains('text-block-stroke-color')) {
        updateTextPreview();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('B52 Memes loaded');
});