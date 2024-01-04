document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('createAccountForm');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const accountId = form.querySelector('[name="account-id"]').value;
        const password = form.querySelector('[name="password"]').value;

        const postData = {
            "account-id": accountId,
            "password": password
        };

        try {
            const response = await fetch('http://localhost:5000/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || response.statusText);
            }

            const data = await response.json();
            const originalAccountId = data['account-id'];
            const modifiedAccountId = data['modified-account-id'];

            alert('Konto erfolgreich erstellt!\nOriginal-Konto-ID: ' + originalAccountId + '\nGeänderte Konto-ID: ' + modifiedAccountId);
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
