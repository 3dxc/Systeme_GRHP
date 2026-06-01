/**
 * Alterne l'affichage du formulaire entre la Connexion et l'Inscription
 * @param {string} mode - 'login' ou 'register'
 */
function switchForm(mode) {
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const formTitle = document.getElementById('form-title');
    const submitBtn = document.getElementById('submit-btn');
    const registerFields = document.querySelectorAll('.id-register-only');
    const nameInput = document.getElementById('user-name');

    // Sécurité au cas où certains éléments n'existent pas encore dans le DOM
    if (!tabLogin || !tabRegister || !formTitle || !submitBtn) return;

    if (mode === 'register') {
        // Mode Inscription
        tabLogin.classList.remove('active');
        tabRegister.classList.add('active');
        formTitle.innerText = "Inscription";
        submitBtn.innerText = "S'inscrire";
        submitBtn.className = "w-full py-2.5 bg-orange-600 hover:bg-orange-700 text-white text-sm font-bold rounded transition duration-200 shadow-sm";
        
        // Afficher le champ Nom complet
        registerFields.forEach(field => field.classList.remove('hidden'));
        if (nameInput) nameInput.setAttribute('required', 'true');
    } else {
        // Mode Connexion
        tabRegister.classList.remove('active');
        tabLogin.classList.add('active');
        formTitle.innerText = "Connexion";
        submitBtn.innerText = "Se connecter";
        submitBtn.className = "w-full py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-bold rounded transition duration-200 shadow-sm";
        
        // Masquer le champ Nom complet
        registerFields.forEach(field => field.classList.add('hidden'));
        if (nameInput) nameInput.removeAttribute('required');
    }
}

/**
 * Intercepte la soumission du formulaire et redirige selon le profil choisi
 */
function handleSubmit(event) {
    event.preventDefault(); 
    
    const profileElement = document.getElementById('user-profile');
    const emailElement = document.getElementById('user-email');
    const tabRegister = document.getElementById('tab-register');

    if (!profileElement) return;

    const profile = profileElement.value;
    const email = emailElement ? emailElement.value : '';
    const isRegister = tabRegister ? tabRegister.classList.contains('active') : false;

    // Message de test combiné
    console.log(`Action : ${isRegister ? 'Inscription' : 'Connexion'} | Profil : ${profile} | Email : ${email}`);
    
    // Redirection en dur (car le JS statique ne comprend pas le template tag de Django)
    // Remplacez '/liste/' ou '/dashboard/...' par les vrais chemins configurés dans vos urls.py
    switch (profile) {
        case 'admin':
            window.location.href = "/dashboard-admin/"; 
            break;
        case 'manager':
            window.location.href = "/dashboard-manager/";
            break;
        case 'agent':
            window.location.href = "/dashboard-agent/";
            break;
        case 'comptable':
            window.location.href = "/dashboard-comptable/";
            break;
        default:
            alert("Veuillez sélectionner un profil valide.");
    }
}