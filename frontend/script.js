document.getElementById("loanForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    age: parseInt(document.getElementById("age").value),
    emp_length: parseInt(document.getElementById("emp_length").value),
    annual_inc: parseFloat(document.getElementById("annual_inc").value),
    dti: parseFloat(document.getElementById("dti").value),
    credit_score: parseFloat(document.getElementById("credit_score").value),
    loan_amnt: parseFloat(document.getElementById("loan_amnt").value),
    int_rate: parseFloat(document.getElementById("int_rate").value),
    loan_tenure: document.getElementById("loan_tenure").value
  };

  const resultSection = document.getElementById("resultSection");
  const riskCard = document.getElementById("riskCard");
  const bankList = document.getElementById("bankList");

  resultSection.classList.remove("hidden");
  riskCard.innerHTML = "⏳ Analyzing your profile...";

  try {
    const response = await fetch("http://127.0.0.1:8080/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const res = await response.json();

    if (!response.ok) throw new Error(res.detail || "API error");

    riskCard.innerHTML = `
      <h3>📊 Risk Score</h3>
      <p><strong>${res["risk_score (%)"]}%</strong></p>
    `;

    bankList.innerHTML = "";
    res.recommended_banks.forEach(bank => {
      const card = document.createElement("div");
      card.classList.add("card");
      card.innerHTML = `
        <h4>${bank["Bank Name"]}</h4>
        <p>💰 Interest: ${bank["Interest Rate (%)"]}%</p>
        <p>✅ Suitability: ${(bank["suitability_score"] * 100).toFixed(1)}%</p>
      `;
      bankList.appendChild(card);
    });

  } catch (error) {
    riskCard.innerHTML = `<p style="color:red;">❌ Error: ${error.message}</p>`;
    bankList.innerHTML = "";
  }
});
