document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const submitBtn = document.getElementById('submit-btn');
    const resetBtn = document.getElementById('reset-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const copyJsonBtn = document.getElementById('copy-json-btn');
    const copyIcon = document.getElementById('copy-icon');
    const successIcon = document.getElementById('success-icon');

    const uploadArea = document.getElementById('upload-area');
    const previewArea = document.getElementById('preview-area');
    const resultArea = document.getElementById('result-area');
    const uploadError = document.getElementById('upload-error');

    const fileNameEl = document.getElementById('file-name');
    const fileDetailsEl = document.getElementById('file-details');

    const loadingSpinner = document.getElementById('loading-spinner');
    const resultWrapper = document.getElementById('result-content');
    const statusMessageContainer = document.getElementById('status-message');
    const dataFieldsContainer = document.getElementById('data-fields');
    const jsonResultWrapper = document.getElementById('json-result-wrapper');
    const jsonCodeEl = jsonResultWrapper.querySelector('code');

    const apiUrl = dropZone.dataset.apiUrl;
    let selectedFile = null;
    let extractedData = {};

    const icons = {
        success: `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`,
        warning: `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>`,
        error: `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>`
    };

    const showView = (view) => {
        [uploadArea, previewArea, resultArea].forEach(el => el.classList.add('hidden'));
        view.classList.remove('hidden');
    };

    const resetUI = () => {
        selectedFile = null;
        extractedData = {};
        fileInput.value = '';
        submitBtn.disabled = false;
        resetBtn.classList.add('hidden');
        statusMessageContainer.innerHTML = '';
        uploadError.classList.add('hidden');
        showView(uploadArea);
    };

    const formatBytes = (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-zone--over');
    });
    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => dropZone.classList.remove('drop-zone--over'));
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-zone--over');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
    cancelBtn.addEventListener('click', resetUI);
    resetBtn.addEventListener('click', resetUI);

    function handleFile(file) {
        uploadError.classList.add('hidden');
        const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
            uploadError.textContent = `Tipo de arquivo não suportado: "${fileExtension}". Por favor, envie um PDF ou imagem.`;
            uploadError.classList.remove('hidden');
            fileInput.value = '';
            return;
        }
        selectedFile = file;
        fileNameEl.textContent = file.name;
        fileDetailsEl.textContent = `${file.type} - ${formatBytes(file.size)}`;
        showView(previewArea);
    }

    submitBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        submitBtn.disabled = true;
        showView(resultArea);
        loadingSpinner.classList.remove('hidden');
        resultWrapper.style.display = 'none';
        statusMessageContainer.innerHTML = '';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(apiUrl, { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Ocorreu um erro desconhecido na extração.');
            }
            displaySuccess(data);
        } catch (error) {
            displayError(error.message);
        } finally {
            loadingSpinner.classList.add('hidden');
            resultWrapper.style.display = 'block';
            resetBtn.classList.remove('hidden');
        }
    });

    copyJsonBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(jsonCodeEl.textContent).then(() => {
            copyIcon.classList.add('hidden');
            successIcon.classList.remove('hidden');
            setTimeout(() => {
                copyIcon.classList.remove('hidden');
                successIcon.classList.add('hidden');
            }, 2000);
        });
    });

    const updateJsonView = () => {
        jsonCodeEl.textContent = JSON.stringify(extractedData, null, 2);
    };

    const createEditableField = (key, value) => {
        const fieldId = `field-${key}`;
        const hasValue = value !== null && value !== '' && value.trim() !== '';
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        const fieldContainer = document.createElement('div');
        
        const wrapper = document.createElement('div');
        wrapper.className = 'flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 p-3 bg-slate-50 rounded-lg border transition-colors';

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'flex items-center gap-3 flex-grow';

        const icon = document.createElement('div');
        icon.className = `w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${hasValue ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'}`;
        icon.innerHTML = hasValue ? icons.success : icons.warning;

        const labelElWrapper = document.createElement('div');
        labelElWrapper.className = 'flex-grow';
        
        const labelEl = document.createElement('label');
        labelEl.htmlFor = fieldId;
        labelEl.className = 'text-sm font-medium text-slate-500';
        labelEl.textContent = label;

        const textDisplay = document.createElement('span');
        textDisplay.id = `display-${fieldId}`;
        textDisplay.className = `block ${hasValue ? 'text-slate-800' : 'text-slate-500 italic'} font-semibold break-all`;
        textDisplay.textContent = value || 'Não preenchido';

        const input = document.createElement('input');
        input.type = 'text';
        input.id = fieldId;
        input.value = value || '';
        input.className = 'hidden w-full bg-transparent text-slate-800 font-semibold focus:outline-none';
        
        labelElWrapper.append(labelEl, textDisplay, input);

        const errorMsg = document.createElement('div');
        errorMsg.id = `error-${fieldId}`;
        errorMsg.className = 'text-red-600 text-xs mt-1 ml-9 hidden';

        if (key === 'cnpj_prestador') {
            input.placeholder = "Digite apenas os números";
            input.setAttribute('maxlength', '18');
            input.addEventListener('input', (e) => {
                let v = e.target.value.replace(/\D/g, '');
                v = v.replace(/^(\d{2})(\d)/, '$1.$2');
                v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
                v = v.replace(/\.(\d{3})(\d)/, '.$1/$2');
                v = v.replace(/(\d{4})(\d)/, '$1-$2');
                e.target.value = v;
            });
        } else {
            input.placeholder = "Digite o nome do prestador";
        }

        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.className = 'edit-btn flex-shrink-0 bg-slate-200 text-slate-700 text-sm font-bold py-1 px-3 rounded-md hover:bg-slate-300 transition-colors flex items-center gap-1.5';
        editButton.innerHTML = `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"/></svg><span>Editar</span>`;
        
        const enterEditMode = () => {
            wrapper.classList.remove('border-red-500', 'border-green-500', 'bg-red-50', 'bg-green-50');
            errorMsg.classList.add('hidden');
            textDisplay.classList.add('hidden');
            input.classList.remove('hidden');
            input.focus();
            input.select();
            editButton.innerHTML = `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg><span>Salvar</span>`;
            editButton.classList.remove('bg-slate-200', 'hover:bg-slate-300');
            editButton.classList.add('bg-purple-600', 'text-white', 'hover:bg-purple-700');
        };

        const exitEditMode = (force = false) => {
            let isValid = true;
            let finalValue = input.value.trim();

            if (key === 'cnpj_prestador') {
                const numbers = finalValue.replace(/\D/g, '');
                if (finalValue === '') {
                    isValid = false;
                    errorMsg.textContent = 'O CNPJ não pode ficar em branco.';
                } else if (numbers.length !== 14) {
                    isValid = false;
                    errorMsg.textContent = 'Formato esperado: XX.XXX.XXX/XXXX-XX (14 dígitos).';
                }
            } else if (key === 'nome_prestador') {
                if (finalValue === '') {
                    isValid = false;
                    errorMsg.textContent = 'O nome do prestador não pode ficar em branco.';
                }
            }

            if (force || isValid) {
                if (isValid) {
                    wrapper.classList.remove('border-red-500', 'bg-red-50');
                    wrapper.classList.add('border-green-500');
                    icon.className = 'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-green-100 text-green-600';
                    icon.innerHTML = icons.success;
                    extractedData[key] = finalValue;
                    updateJsonView();
                }
                errorMsg.classList.add('hidden');
                textDisplay.textContent = finalValue || 'Não preenchido';
                textDisplay.classList.remove('hidden');
                input.classList.add('hidden');
                editButton.innerHTML = `<svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"/></svg><span>Editar</span>`;
                editButton.classList.remove('bg-purple-600', 'text-white', 'hover:bg-purple-700');
                editButton.classList.add('bg-slate-200', 'hover:bg-slate-300');
            } else {
                wrapper.classList.remove('border-green-500');
                wrapper.classList.add('border-red-500', 'bg-red-50');
                icon.className = 'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-red-100 text-red-700';
                icon.innerHTML = icons.error;
                errorMsg.classList.remove('hidden');
            }
        };

        editButton.addEventListener('click', () => {
            if (input.classList.contains('hidden')) enterEditMode();
            else exitEditMode();
        });

        input.addEventListener('blur', () => {
            if (!input.classList.contains('hidden')) exitEditMode();
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') exitEditMode();
            else if (e.key === 'Escape') {
                input.value = extractedData[key] || '';
                exitEditMode(true);
            }
        });

        contentWrapper.append(icon, labelElWrapper);
        wrapper.append(contentWrapper, editButton);
        fieldContainer.append(wrapper, errorMsg);

        return fieldContainer;
    };

    function displaySuccess(data) {
        extractedData = data;
        dataFieldsContainer.innerHTML = '';
        Object.entries(data).forEach(([key, value]) => {
            const field = createEditableField(key, value);
            dataFieldsContainer.appendChild(field);
        });
        updateJsonView();
        jsonResultWrapper.classList.remove('hidden');
    }

    function displayError(message) {
        statusMessageContainer.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
                <p class="font-bold">Falha na Extração</p>
                <p>${message}</p>
            </div>`;
        dataFieldsContainer.innerHTML = '';
        jsonResultWrapper.classList.add('hidden');
    }
});