document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('challengeResponseForm');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append('account-id', document.getElementById('accountId').value);
        formData.append('challenge-response', document.getElementById('challengeResponse').value);

        try {
            const response = await fetch('http://localhost:5000/respond_challenge', {
                method: 'POST',
                body: formData
            });

            console.log('Response headers:', response.headers);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || response.statusText);
            }

            const data = await response.json();
            alert('Response successful: ' + data.message);
        } catch (error) {
            let errorMessage = 'Fehler bei der Anfrage: ';
            if (error.message === 'Failed to fetch') {
                errorMessage += 'Keine Antwort vom Server. Bitte überprüfen Sie Ihre Netzwerkverbindung.';
            } else {
                errorMessage += error.message;
            }
            alert(errorMessage);
        }
    });
});
