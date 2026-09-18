// Base URL of the FastAPI backend. Twilio credentials never live here —
// this script only talks to our own backend, never to Twilio directly.
const API_BASE_URL = "http://127.0.0.1:8000";

const verifySection = document.getElementById("verify-section");
const phoneInput = document.getElementById("phone-number");
const otpInput = document.getElementById("otp-code");
const sendSmsBtn = document.getElementById("send-sms-btn");
const sendWhatsappBtn = document.getElementById("send-whatsapp-btn");
const verifyBtn = document.getElementById("verify-btn");
const statusMessage = document.getElementById("status-message");

function showStatus(message, isError) {
  statusMessage.textContent = message;
  statusMessage.className = isError ? "error" : "success";
}

// FastAPI (pydantic) validation errors come back as detail: [{msg, loc, ...}, ...]
// instead of a plain string. Without this, showStatus would render that array
// as "[object Object]". This turns it into a readable message.
function extractErrorMessage(data, fallback) {
  const detail = data && data.detail;

  if (!detail) {
    return fallback;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => (item && typeof item === "object" ? item.msg : item))
      .filter(Boolean)
      .join(" ") || fallback;
  }

  return fallback;
}

// Browser -> FastAPI -> Twilio Verify -> OTP (SMS or WhatsApp)
async function sendOtp(channel) {
  const phoneNumber = phoneInput.value.trim();
  const channelLabel = channel === "whatsapp" ? "WhatsApp" : "SMS";
  showStatus(`Sending ${channelLabel} OTP...`, false);

  // Disable both channel buttons while a send is in flight to prevent
  // accidental repeated OTP requests.
  sendSmsBtn.disabled = true;
  sendWhatsappBtn.disabled = true;

  try {
    const response = await fetch(`${API_BASE_URL}/api/otp/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber, channel }),
    });

    const data = await response.json();

    if (!response.ok) {
      showStatus(extractErrorMessage(data, "Failed to send OTP."), true);
      return;
    }

    showStatus(`Verification code sent via ${channelLabel}.`, false);
    verifySection.classList.remove("hidden");
  } catch (err) {
    showStatus("Could not reach the backend.", true);
  } finally {
    sendSmsBtn.disabled = false;
    sendWhatsappBtn.disabled = false;
  }
}

sendSmsBtn.addEventListener("click", () => sendOtp("sms"));
sendWhatsappBtn.addEventListener("click", () => sendOtp("whatsapp"));

// User enters OTP -> FastAPI -> Twilio Verify verification check
verifyBtn.addEventListener("click", async () => {
  const phoneNumber = phoneInput.value.trim();
  const code = otpInput.value.trim();
  showStatus("Verifying OTP...", false);

  // Disable while a verification check is in flight.
  verifyBtn.disabled = true;

  try {
    const response = await fetch(`${API_BASE_URL}/api/otp/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber, code }),
    });

    const data = await response.json();

    if (!response.ok) {
      showStatus(extractErrorMessage(data, "Failed to verify OTP."), true);
      return;
    }

    if (data.success) {
      showStatus("OTP VERIFIED SUCCESSFULLY", false);
    } else {
      showStatus(`Verification not approved (status: ${data.status}).`, true);
    }
  } catch (err) {
    showStatus("Could not reach the backend.", true);
  } finally {
    verifyBtn.disabled = false;
  }
});
