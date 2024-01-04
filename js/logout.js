function logout() {
    sessionStorage.removeItem('account-id');
    //sessionStorage.clear();
    window.location.href = 'login.html';
}