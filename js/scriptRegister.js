document.addEventListener('DOMContentLoaded', function () {
    if (!sessionStorage.getItem('account-id')) {
        window.location.href = 'login.html';
    }

    var accountIdInput = document.getElementById('accountId');
    var accountId = sessionStorage.getItem('account-id');

    if (accountId) {
        accountIdInput.value = accountId;
        accountIdInput.readOnly = true;
    }

    const form = document.getElementById('registerForm');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const accountID = form.querySelector('[name="account-id"]').value;
        const password = form.querySelector('[name="password"]').value;
        const emailAddress = form.querySelector('[name="email-address"]').value;
        const keyID = form.querySelector('[name="key-id"]').value;
        const pgpKey = form.querySelector('[name="pgp-key"]').files[0];

        const formData = new FormData();
        formData.append('account-id', accountID);
        formData.append('password', password);
        formData.append('email-address', emailAddress);
        formData.append('key-id', keyID);
        formData.append('pgp-key', pgpKey);

        try {
            const response = await fetch('http://127.0.0.1:5000/register', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || response.statusText);
            }

            const data = await response.json();
            alert('Registrierung erfolgreich!\nNachricht: ' + data.message);
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
