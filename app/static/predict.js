document.addEventListener('DOMContentLoaded', function() {
    // Cache for driver images
    const imageCache = new Map();
    
    // Initialize image cache with all driver images from the template
    const template = document.getElementById('driver-template');
    template.content.querySelectorAll('.driver-info img').forEach(img => {
        if (!imageCache.has(img.src)) {
            const cachedImg = new Image();
            cachedImg.src = img.src;
            cachedImg.alt = img.alt;
            cachedImg.className = img.className;
            cachedImg.onerror = img.onerror;
            imageCache.set(img.src, cachedImg);
        }
    });

    // SVG icons for status indicators
    const statusIcons = {
        loading: `<svg class="status-indicator loading" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v2"></path></svg>`,
        success: `<svg class="status-indicator success" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"></path></svg>`,
        error: `<svg class="status-indicator error" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`
    };

    function showStatus(element, status) {
        let statusContainer = element.querySelector('.status-container');
        if (!statusContainer) {
            statusContainer = document.createElement('div');
            statusContainer.className = 'status-container';
            element.appendChild(statusContainer);
        }

        statusContainer.innerHTML = statusIcons[status] || '';
        
        if (status !== 'loading') {
            setTimeout(() => {
                statusContainer.innerHTML = '';
            }, 3000);
        }
    }

    const dropdowns = document.querySelectorAll('.custom-dropdown');
    let activeDropdown = null;

    // Function to get selected drivers in a form
    function getSelectedDrivers(form) {
        const inputs = form.querySelectorAll('input[type="hidden"]');
        return Array.from(inputs)
            .map(input => input.value)
            .filter(value => value !== '0' && value !== '' && value !== 'None' && value !== 'No DNF');
    }

    // Populate all dropdowns with driver items from template
    dropdowns.forEach(dropdown => {
        const driverItems = dropdown.querySelector('.driver-items');
        if (driverItems) {
            // For DNF dropdown, keep the existing "No DNF" option and add drivers
            const existingContent = driverItems.innerHTML;
            const templateContent = template.content.cloneNode(true);
            driverItems.innerHTML = existingContent;
            templateContent.querySelectorAll('.dropdown-item').forEach(item => {
                driverItems.appendChild(item.cloneNode(true));
            });
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.custom-dropdown')) {
            closeAllDropdowns();
        }
    });

    // Function to update visual indication of selected drivers
    function updateSelectedDriversVisual(form) {
        const allInputs = form.querySelectorAll('input[type="hidden"]');
        const bonusInputs = ['fastestlap', 'dnf', 'dod'];
        const selectedDrivers = new Map();

        // Collect all selected drivers and their positions
        allInputs.forEach(input => {
            if (!bonusInputs.includes(input.name) && input.value !== '0' && input.value !== '' && input.value !== 'None') {
                selectedDrivers.set(input.value, input);
            }
        });

        // Update visual indication for all dropdowns in the form
        form.querySelectorAll('.dropdown-item').forEach(item => {
            const driverId = item.dataset.value;
            const isSelectedElsewhere = selectedDrivers.has(driverId) && 
                                      selectedDrivers.get(driverId) !== item.closest('.custom-dropdown').querySelector('input[type="hidden"]');
            item.classList.toggle('selected-elsewhere', isSelectedElsewhere);
        });
    }

    dropdowns.forEach(function(dropdown) {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');
        const search = dropdown.querySelector('.driver-search');
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');
        
        // Set initial value if exists
        const initialValue = dropdown.dataset.value;
        if (initialValue) {
            const selectedItem = Array.from(items).find(item => item.dataset.value === initialValue);
            if (selectedItem) {
                updateDropdownSelection(toggle, selectedItem, hiddenInput);
            }
        }

        // Toggle dropdown
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (activeDropdown && activeDropdown !== dropdown) {
                closeDropdown(activeDropdown);
            }

            const isOpen = menu.classList.contains('show');
            
            if (!isOpen) {
                openDropdown(dropdown);
                // Update visual indication when opening dropdown
                const form = dropdown.closest('form');
                if (form) {
                    updateSelectedDriversVisual(form);
                }
            } else {
                closeDropdown(dropdown);
            }
        });

        // Handle item selection
        items.forEach(function(item) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                // Find if this driver is already selected somewhere else in the form
                const form = dropdown.closest('form');
                const allInputs = form.querySelectorAll('input[type="hidden"]');
                const selectedDriverId = item.dataset.value;
                const bonusInputs = ['fastestlap', 'dnf', 'dod'];
                const currentInput = hiddenInput;

                // Don't handle duplicates for bonus predictions
                if (!bonusInputs.includes(currentInput.name)) {
                    let foundConflict = false;
                    allInputs.forEach(input => {
                        if (input !== currentInput && 
                            input.value === selectedDriverId && 
                            !bonusInputs.includes(input.name)) {
                            foundConflict = true;
                            // Only attempt to swap if both positions have valid drivers
                            const currentDriverId = currentInput.value;
                            const otherDropdown = input.closest('.custom-dropdown');
                            const otherToggle = otherDropdown.querySelector('.dropdown-toggle');
                            
                            // Reset the other position to "Select Driver" by default
                            input.value = '0';
                            otherToggle.innerHTML = 'Select Driver';

                            // Only attempt swap if current position has a valid driver
                            if (currentDriverId && currentDriverId !== '0' && currentDriverId !== '') {
                                // Find the dropdown item for the current driver in the other dropdown
                                const otherItems = otherDropdown.querySelectorAll('.dropdown-item');
                                const currentDriverItem = Array.from(otherItems).find(i => i.dataset.value === currentDriverId);
                                
                                if (currentDriverItem) {
                                    // Update the other dropdown with current driver
                                    updateDropdownSelection(otherToggle, currentDriverItem, input);
                                }
                            }
                        }
                    });
                }

                // Always update the current dropdown with the selected driver
                updateDropdownSelection(toggle, item, hiddenInput);
                closeDropdown(dropdown);
                
                // Submit the form using fetch with CSRF token
                const container = dropdown.closest('.prediction-input');
                if (form && container) {
                    // Small delay to ensure all DOM updates are complete
                    setTimeout(() => {
                        showStatus(container, 'loading');
                        const formData = new FormData(form);
                        
                        // Verify no duplicates before submitting (excluding bonus predictions)
                        const bonusInputs = ['fastestlap', 'dnf', 'dod'];
                        const values = Array.from(formData.entries())
                            .filter(([key]) => !bonusInputs.includes(key)) // Filter out bonus predictions
                            .map(([_, value]) => value)
                            .filter(v => v !== '0' && v !== '' && v !== 'None' && v !== 'No DNF');
                        
                        const duplicates = values.filter((v, i, a) => a.indexOf(v) !== i);
                            
                        if (duplicates.length > 0) {
                            showStatus(container, 'error');
                            console.error('Duplicate values found:', duplicates);
                            return;
                        }

                        fetch(form.action, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to save prediction');
                            }
                            showStatus(container, 'success');
                            // Update visual indication after successful save
                            updateSelectedDriversVisual(form);
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            showStatus(container, 'error');
                            // Reset the selection
                            hiddenInput.value = '0';
                            toggle.innerHTML = 'Select Driver';
                            // Update visual indication after error
                            updateSelectedDriversVisual(form);
                        });
                    }, 50); // Small delay to ensure DOM updates are complete
                }
            });
        });

        // Handle search
        if (search) {
            search.addEventListener('click', function(e) {
                e.stopPropagation();
            });

            search.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                items.forEach(function(item) {
                    const driverName = item.querySelector('.driver-name')?.textContent.toLowerCase() || '';
                    const teamName = item.querySelector('.driver-team')?.textContent.toLowerCase() || '';
                    const isMatch = driverName.includes(searchTerm) || teamName.includes(searchTerm);
                    item.classList.toggle('hidden', !isMatch);
                });
            });

            // Prevent dropdown from closing when clicking in search field
            search.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    });

    // Handle head-to-head matches
    const headToHeadMatches = document.querySelectorAll('.head-to-head-match');
    const headToHeadForm = document.getElementById('headtohead-form');

    headToHeadMatches.forEach(match => {
        const buttons = match.querySelectorAll('.driver-button');
        
        buttons.forEach(button => {
            if (button.getAttribute('data-selected') === 'true') {
                button.style.backgroundColor = 'green';
            } else {
                button.style.backgroundColor = 'red';
            }

            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (!headToHeadForm.classList.contains('disabled')) {
                    buttons.forEach(resetButton => {
                        resetButton.style.backgroundColor = 'red';
                        resetButton.setAttribute('data-selected', 'false');
                    });

                    this.style.backgroundColor = 'green';
                    this.setAttribute('data-selected', 'true');

                    showStatus(match, 'loading');

                    fetch(headToHeadForm.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'driver_selection=' + encodeURIComponent(this.value) + '&csrf_token=' + encodeURIComponent(headToHeadForm.querySelector('input[name="csrf_token"]').value)
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        showStatus(match, 'success');
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showStatus(match, 'error');
                    });
                }
            });
        });
    });

    function openDropdown(dropdown) {
        const menu = dropdown.querySelector('.dropdown-menu');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const search = dropdown.querySelector('.driver-search');

        menu.style.display = "flex";
        
        menu.classList.add('show');
        toggle.classList.add('active');
        
        if (search) {
            search.value = '';
        }
        
        activeDropdown = dropdown;
    }

    function closeDropdown(dropdown) {
        if (!dropdown) return;
        
        const menu = dropdown.querySelector('.dropdown-menu');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const items = dropdown.querySelectorAll('.dropdown-item');

        menu.style.display = "none";
        
        menu.classList.remove('show');
        toggle.classList.remove('active');
        
        items.forEach(item => item.classList.remove('hidden'));
        
        if (activeDropdown === dropdown) {
            activeDropdown = null;
        }
    }

    function closeAllDropdowns() {
        dropdowns.forEach(closeDropdown);
    }

    function updateDropdownSelection(toggle, selectedItem, hiddenInput) {
        const driverInfo = selectedItem.querySelector('.driver-info').cloneNode(true);
        const originalImg = driverInfo.querySelector('img');
        
        // Replace the cloned image with cached version if available
        if (originalImg && imageCache.has(originalImg.src)) {
            const cachedImg = imageCache.get(originalImg.src).cloneNode(true);
            originalImg.parentNode.replaceChild(cachedImg, originalImg);
        }
        
        toggle.innerHTML = '';
        toggle.appendChild(driverInfo);
        
        if (hiddenInput) {
            hiddenInput.value = selectedItem.dataset.value;
        }
        
        // Mark the selected item
        const allItems = selectedItem.closest('.dropdown-menu').querySelectorAll('.dropdown-item');
        allItems.forEach(item => item.classList.remove('selected'));
        selectedItem.classList.add('selected');
    }

    function updateCountdown(element) {
        const deadline = new Date(element.dataset.deadline).getTime();
        const now = new Date().getTime();
        const timeLeft = deadline - now;

        if (timeLeft <= 0) {
            element.innerHTML = '<div class="expired-text">Predictions closed</div>';
            element.closest('.deadline-box').classList.add('expired');
            return;
        }

        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        element.querySelector('.days').textContent = String(days).padStart(2, '0');
        element.querySelector('.hours').textContent = String(hours).padStart(2, '0');
        element.querySelector('.minutes').textContent = String(minutes).padStart(2, '0');
        element.querySelector('.seconds').textContent = String(seconds).padStart(2, '0');
    }

    // Initialize countdowns
    const countdowns = document.querySelectorAll('.countdown');
    countdowns.forEach(countdown => {
        if (countdown.querySelector('.countdown-timer')) {
            updateCountdown(countdown);
            setInterval(() => updateCountdown(countdown), 1000);
        }
    });
}); 