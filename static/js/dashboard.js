const elementoGrafico = document.getElementById("graficoFinanceiro");

const totalReceitas = Number(elementoGrafico.dataset.receitas);
const totalDespesas = Number(elementoGrafico.dataset.despesas);

const areaGrafico = document.querySelector(".area-grafico");


if (totalReceitas === 0 && totalDespesas === 0) {

    areaGrafico.innerHTML = `
        <p class="mensagem-sem-dados">
            Nenhuma movimentação financeira registrada.
        </p>
    `;

} else {

    
    const dadosFinanceiros = {
        labels: ["Receitas", "Despesas"],

        datasets: [{
            data: [totalReceitas, totalDespesas],

            backgroundColor: [
                "#183B2B",
                "#C6A15B"
            ],

            borderWidth: 0
        }]
    };

    
    const configuracaoGrafico = {
        type: "doughnut",

        data: dadosFinanceiros,

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: "bottom",

                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },

            cutout: "65%"
        }
    };

    new Chart(elementoGrafico, configuracaoGrafico);
}