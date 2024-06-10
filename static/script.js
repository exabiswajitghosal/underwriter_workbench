let submissionId = null;

// Function to call the first API endpoint to read emails
async function readEmails() {
    const response = await fetch('/api/fetch_email');
    if (!response.ok) {
        throw new Error('Failed to read emails');
    }
    const data = await response.json();
    return data;
}

// Function to call the second API endpoint to extract data
async function extractData(submissionId) {
    const response = await fetch('/api/generate_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ submission_id: submissionId })
    });
    if (!response.ok) {
        throw new Error('Failed to extract data');
    }
    const data = await response.json();
    return data;
}

// Function to create a downloadable file
function createDownloadableFile(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Handle extract files button click
document.getElementById('extractBtn').addEventListener('click', async () => {
    const extractResponseElement = document.getElementById('extractResponse');
    try {
        if (submissionId) {
            const extractedData = await extractData(submissionId);
            createDownloadableFile(extractedData);
            extractResponseElement.textContent = 'Data extracted successfully. Ready to download.';
            document.getElementById('downloadBtn').disabled = false;
        }
    } catch (error) {
        extractResponseElement.textContent = `Error: ${error.message}`;
    }
});

// Handle download data button click
document.getElementById('downloadBtn').addEventListener('click', async () => {
    try {
        const emailData = await readEmails();
        const extractedData = await extractData(emailData.submission_id);
        createDownloadableFile(extractedData);
    } catch (error) {
        console.error('Error:', error);
    }
});
