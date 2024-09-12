document.addEventListener('DOMContentLoaded', () => {
    const tweetUrlInput = document.getElementById('tweetUrl');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const summaryText = document.getElementById('summaryText');
    const combinedText = document.getElementById('combinedText');
    const copyBtns = document.querySelectorAll('.copy-btn');

    summarizeBtn.addEventListener('click', summarizeThread);
    copyBtns.forEach(btn => btn.addEventListener('click', copyText));

    async function summarizeThread() {
        const url = tweetUrlInput.value.trim();
        if (!url) {
            alert('Please enter a valid Twitter thread URL');
            return;
        }

        summarizeBtn.disabled = true;
        summarizeBtn.textContent = 'Summarizing...';

        try {
            const response = await fetch('https://qzry3wuxnk.execute-api.eu-north-1.amazonaws.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tweet_url: url }),
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            summaryText.textContent = data.summary;
            combinedText.textContent = data.combined_text;
        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        } finally {
            summarizeBtn.disabled = false;
            summarizeBtn.textContent = 'Summarize';
        }
    }

    function copyText(event) {
        const targetId = event.target.getAttribute('data-target');
        const textToCopy = document.getElementById(targetId).textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
});
