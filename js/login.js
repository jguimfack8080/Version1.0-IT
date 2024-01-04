document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const accountId = loginForm.querySelector('[name="account-id"]').value;
        const password = loginForm.querySelector('[name="password"]').value;

        const formData = new FormData();
        formData.append('account-id', accountId);
        formData.append('password', password);

        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error);
            }

            sessionStorage.setItem('account-id', accountId);
            window.location.href = 'index.html?Konto-id=' + encodeURIComponent(accountId);
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
