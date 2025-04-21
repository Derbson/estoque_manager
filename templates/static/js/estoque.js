// Funções globais para o sistema

// Confirmação antes de ações importantes
function confirmAction(message) {
    return confirm(message || 'Tem certeza que deseja realizar esta ação?');
}

// Formata números para o padrão brasileiro
function formatNumber(number, decimals = 2) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

// Inicialização de tooltips
$(function () {
    $('[data-bs-toggle="tooltip"]').tooltip();
});