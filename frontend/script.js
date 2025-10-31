document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("loanForm");
  const resultDiv = document.getElementById("result");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = {
      name: document.getElementById("name").value,
      age: parseFloat(document.getElementById("age").value),
      emp_length: parseFloat(document.getElementById("emp_length").value),
      employment_status: document.getElementById("employment_status").value,
      annual_inc: parseFloat(document.getElementById("annual_inc").value),
      existing_debt: parseFloat(document.getElementById("existing_debt").value),
      credit_score: parseFloat(document.getElementById("credit_score").value),
      loan_amnt: parseFloat(document.getElementById("loan_amnt").value),
      loan_type: document.getElementById("loan_type").value,
      loan_tenure: document.getElementById("loan_tenure").value
    };

    try {
      const response = await fetch("http://127.0.0.1:8081/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();

      const risk = data["risk_score (%)"];
      let verdict = "";
      let barColor = "";

      if (risk < 25) {
        verdict = "✅ Low Risk — Likely Approved";
        barColor = "bg-success";
      } else if (risk < 60) {
        verdict = "⚠️ Moderate Risk — Review Needed";
        barColor = "bg-warning";
      } else {
        verdict = "❌ High Risk — Likely Rejected";
        barColor = "bg-danger";
      }

      resultDiv.innerHTML = `
        <div class="result-card">
          <h4>${verdict}</h4>
          <div class="progress mt-2">
            <div class="progress-bar ${barColor}" role="progressbar" style="width: ${risk}%;">
              ${risk}%
            </div>
          </div>
          <h5 class="mt-3">🏦 Recommended Banks:</h5>
          <div class="bank-list">
            ${data.recommended_banks.map(
              b => `<div class="bank-item"><strong>${b["Bank Name"]}</strong> — 
              ${b["Interest Rate (%)"]}% (Suitability: ${(b["suitability_score"]*100).toFixed(1)}%)</div>`
            ).join("")}
          </div>
        </div>
      `;
    } catch (error) {
      console.error("Error:", error);
      resultDiv.innerHTML = `<p style="color:red;">❌ Error: ${error.message}</p>`;
    }
  });
});
