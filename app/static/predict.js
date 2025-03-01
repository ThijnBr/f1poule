document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.custom-dropdown');
    let activeDropdown = null;

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

        // Toggle dropdown
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            
            if (activeDropdown && activeDropdown !== dropdown) {
                closeDropdown(activeDropdown);
            }

            const isOpen = menu.classList.contains('show');
            
            if (!isOpen) {
                openDropdown(dropdown);
            } else {
                closeDropdown(dropdown);
            }
        });

        // Handle item selection
        items.forEach(function(item) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                updateDropdownSelection(toggle, item, hiddenInput);
                closeDropdown(dropdown);
                
                // Submit the form using fetch with CSRF token
                const form = dropdown.closest('form');
                if (form) {
                    const formData = new FormData(form);
                    fetch(form.action, {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        // Optionally handle success
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Optionally handle error
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

    function openDropdown(dropdown) {
        const menu = dropdown.querySelector('.dropdown-menu');
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const search = dropdown.querySelector('.driver-search');

        menu.style.display = "flex";
        
        menu.classList.add('show');
        toggle.classList.add('active');
        
        if (search) {
            search.value = '';
            search.focus();
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