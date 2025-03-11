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

    // Function to check if a driver is already selected in a form
    function isDriverSelected(form, driverId, currentInput) {
        const inputs = form.querySelectorAll('input[type="hidden"]');
        const bonusInputs = ['fastestlap', 'dnf', 'dod'];

        // If this is a bonus prediction (fastest lap, DNF, or driver of the day), allow duplicates
        if (bonusInputs.includes(currentInput.name)) {
            return false;
        }

        // For race predictions (top 5), check only against other race predictions
        return Array.from(inputs).some(input => 
            input !== currentInput && 
            input.value === driverId && 
            driverId !== '0' && 
            driverId !== '' && 
            driverId !== 'None' && 
            driverId !== 'No DNF' &&
            !bonusInputs.includes(input.name)
        );
    }

    // Function to update dropdown items based on selected drivers
    function updateDropdownItems(dropdown) {
        const form = dropdown.closest('form');
        const items = dropdown.querySelectorAll('.dropdown-item');
        const hiddenInput = dropdown.querySelector('input[type="hidden"]');

        items.forEach(item => {
            const driverId = item.dataset.value;
            if (isDriverSelected(form, driverId, hiddenInput)) {
                item.classList.add('disabled');
            } else {
                item.classList.remove('disabled');
            }
        });
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

        // Update initial disabled state
        updateDropdownItems(dropdown);

        // Toggle dropdown
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (activeDropdown && activeDropdown !== dropdown) {
                closeDropdown(activeDropdown);
            }

            const isOpen = menu.classList.contains('show');
            
            if (!isOpen) {
                openDropdown(dropdown);
                updateDropdownItems(dropdown);
            } else {
                closeDropdown(dropdown);
            }
        });

        // Handle item selection
        items.forEach(function(item) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                if (item.classList.contains('disabled')) {
                    return;
                }

                updateDropdownSelection(toggle, item, hiddenInput);
                closeDropdown(dropdown);
                
                // Submit the form using fetch with CSRF token
                const form = dropdown.closest('form');
                const container = dropdown.closest('.prediction-input');
                if (form && container) {
                    showStatus(container, 'loading');
                    const formData = new FormData(form);
                    fetch(form.action, {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Duplicate drivers are not allowed');
                        }
                        showStatus(container, 'success');
                        // Update disabled state for all dropdowns in the form
                        form.querySelectorAll('.custom-dropdown').forEach(updateDropdownItems);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showStatus(container, 'error');
                        // Reset the selection
                        hiddenInput.value = '0';
                        toggle.innerHTML = 'Select Driver';
                        // Update disabled state
                        updateDropdownItems(dropdown);
                    });
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
}); 