import React, { useState } from "react";
import "./ValidationCheck.css";

const ValidationCheck = ({ validateConfigs, onValidationSuccess }) => {
    const [validationStatus, setValidationStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleValidation = async () => {
        setLoading(true);
        setValidationStatus(null);

        try {
            const isValid = await validateConfigs();
            if (isValid) {
                setValidationStatus("success");
                onValidationSuccess(); // Move to next step
            } else {
                setValidationStatus("error");
            }
        } catch (error) {
            setValidationStatus("error");
            console.error("Validation error:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="validation-container">
            <h2>Validation Check</h2>
            <p>Ensuring your configurations are correct before starting ingestion.</p>

            {loading && <p className="loading">🔄 Validating...</p>}

            {validationStatus === "success" && <p className="success">✅ Validation Successful!</p>}
            {validationStatus === "error" && <p className="error">❌ Validation Failed. Please check your settings.</p>}

            <button onClick={handleValidation} disabled={loading}>
                {loading ? "Validating..." : "Run Validation"}
            </button>
        </div>
    );
};

export default ValidationCheck;
