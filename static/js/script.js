/* JavaScript personnalisé pour Script Converter */

// Utilitaires généraux
const utils = {
    // Afficher un toast de notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        const toast = this.createToast(message, type);
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Suppression automatique après affichage
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },
    
    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        };
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${iconMap[type] || iconMap.info}"></i>
                <strong class="me-auto ms-2">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        return toast;
    },
    
    // Copier du texte dans le presse-papiers
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copié dans le presse-papiers!', 'success');
        } catch (err) {
            this.showToast('Erreur lors de la copie', 'error');
        }
    },
    
    // Formater la taille de fichier
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Gestion des formulaires
const formManager = {
    // Validation côté client
    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                this.showFieldError(input, 'Ce champ est requis');
                isValid = false;
            } else {
                this.clearFieldError(input);
            }
        });
        
        return isValid;
    },
    
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        let feedback = input.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    },
    
    clearFieldError(input) {
        input.classList.remove('is-invalid');
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    },
    
    // Sauvegarde automatique
    enableAutoSave(form, callback, delay = 2000) {
        const inputs = form.querySelectorAll('input, select, textarea');
        const debouncedSave = utils.debounce(callback, delay);
        
        inputs.forEach(input => {
            input.addEventListener('input', debouncedSave);
            input.addEventListener('change', debouncedSave);
        });
    }
};

// Gestion des fichiers
const fileManager = {
    // Validation de fichier
    validateFile(file, maxSize = 50 * 1024 * 1024, allowedTypes = ['.py', '.pyw']) {
        if (!file) {
            return { valid: false, error: 'Aucun fichier sélectionné' };
        }
        
        if (file.size > maxSize) {
            return { valid: false, error: `Fichier trop volumineux (max ${utils.formatFileSize(maxSize)})` };
        }
        
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(extension)) {
            return { valid: false, error: `Type de fichier non autorisé (${allowedTypes.join(', ')})` };
        }
        
        return { valid: true };
    },
    
    // Lecture de fichier
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(e);
            reader.readAsText(file, 'utf-8');
        });
    },
    
    // Téléchargement de fichier
    downloadText(content, filename) {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
};

// Gestionnaire d'API
const apiManager = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };
        
        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            utils.showToast(`Erreur API: ${error.message}`, 'error');
            throw error;
        }
    },
    
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async postForm(url, formData) {
        return this.request(url, {
            method: 'POST',
            headers: {}, // Laisser le navigateur définir Content-Type pour FormData
            body: formData
        });
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialiser les popovers Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Améliorer les formulaires de téléchargement
    const uploadForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    uploadForms.forEach(form => {
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const validation = fileManager.validateFile(file);
                    if (!validation.valid) {
                        utils.showToast(validation.error, 'error');
                        e.target.value = '';
                        return;
                    }
                    
                    // Afficher les informations du fichier
                    const info = `Fichier: ${file.name} (${utils.formatFileSize(file.size)})`;
                    utils.showToast(info, 'info');
                }
            });
        }
    });
    
    // Améliorer les zones de code
    const codeBlocks = document.querySelectorAll('.code-preview');
    codeBlocks.forEach(block => {
        // Ajouter un bouton de copie
        if (block.textContent.trim()) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'btn btn-sm btn-outline-secondary position-absolute';
            copyBtn.style.top = '10px';
            copyBtn.style.right = '10px';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copier le code';
            
            const container = block.parentNode;
            if (container.style.position !== 'relative') {
                container.style.position = 'relative';
            }
            container.appendChild(copyBtn);
            
            copyBtn.addEventListener('click', () => {
                utils.copyToClipboard(block.textContent);
            });
        }
    });
    
    // Gestion des erreurs globales
    window.addEventListener('error', function(e) {
        console.error('Erreur JavaScript:', e.error);
        utils.showToast('Une erreur inattendue s\'est produite', 'error');
    });
    
    // Gestion des promesses rejetées
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Promesse rejetée:', e.reason);
        utils.showToast('Erreur de réseau ou de traitement', 'error');
    });
});

// Fonctions utilitaires spécifiques à l'application
window.ScriptConverter = {
    utils,
    formManager,
    fileManager,
    apiManager
};