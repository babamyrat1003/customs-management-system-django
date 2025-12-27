// admin.js
document.addEventListener('DOMContentLoaded', function () {
    const violationTypeField = document.querySelector('#id_violation_type');

    const fieldGroups = {
        'legal entity': ['id_company_name','id_company_boss_fullname', 'id_address', 'id_phone'],
        'individual': ['id_violator_name', 'id_violator_surname', 'id_father_name', 'id_date_of_birth', 'id_place_of_birth', 'id_passport_number', 'id_passport_issue_date', 'id_nationality', 'id_violator_address', 'id_phone'],
        'official': ['id_violator_name', 'id_violator_surname', 'id_father_name', 'id_date_of_birth', 'id_place_of_birth', 'id_passport_number', 'id_passport_issue_date', 'id_nationality', 'id_violator_address', 'id_phone'],
    };

    function toggleFields() {
        const selectedType = violationTypeField.value;

        // Hide all fields initially
        Object.values(fieldGroups).flat().forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.closest('.form-row').style.display = 'none';
            }
        });

        // Show fields for the selected type
        if (fieldGroups[selectedType]) {
            fieldGroups[selectedType].forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.closest('.form-row').style.display = '';
                }
            });
        }
    }

    violationTypeField.addEventListener('change', toggleFields);
    toggleFields(); // Initial call to set visibility based on existing value
});
