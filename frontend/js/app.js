// Base URL of the FastAPI backend. Twilio credentials never live here —
// this script only talks to our own backend, never to Twilio directly.
const API_BASE_URL = "http://127.0.0.1:8000";

const verifySection = document.getElementById("verify-section");
const phoneInput = document.getElementById("phone-number");
const otpInput = document.getElementById("otp-code");
const sendBtn = document.getElementById("send-btn");
const verifyBtn = document.getElementById("verify-btn");
const statusMessage = document.getElementById("status-message");

function showStatus(message, isError) {
  statusMessage.textContent = message;
  statusMessage.className = isError ? "error" : "success";
}

// Browser -> FastAPI -> Twilio Verify -> SMS OTP
sendBtn.addEventListener("click", async () => {
  const phoneNumber = phoneInput.value.trim();
  showStatus("Sending OTP...", false);

  try {
    const response = await fetch(`${API_BASE_URL}/api/otp/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber }),
    });

    const data = await response.json();

    if (!response.ok) {
      showStatus(data.detail || "Failed to send OTP.", true);
      return;
    }

    showStatus("Verification code sent.", false);
    verifySection.classList.remove("hidden");
  } catch (err) {
    showStatus("Could not reach the backend.", true);
  }
});

// User enters OTP -> FastAPI -> Twilio Verify verification check
verifyBtn.addEventListener("click", async () => {
  const phoneNumber = phoneInput.value.trim();
  const code = otpInput.value.trim();
  showStatus("Verifying OTP...", false);

  try {
    const response = await fetch(`${API_BASE_URL}/api/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber, code }),
    });

    const data = await response.json();

    if (!response.ok) {
      showStatus(data.detail || "Failed to verify OTP.", true);
      return;
    }

    if (data.success) {
      showStatus("OTP VERIFIED SUCCESSFULLY", false);
    } else {
      showStatus(`Verification not approved (status: ${data.status}).`, true);
    }
  } catch (err) {
    showStatus("Could not reach the backend.", true);
  }
});
