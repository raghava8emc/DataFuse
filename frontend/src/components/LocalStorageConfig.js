import React from "react";
import "./LocalStorageConfig.css";

const LocalStorageConfig = ({ formData, setFormData, setFormatType }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name === "outputPath" ? "output_path" : name]: value, // Rename key
        }));
    };

    const handleFormatChange = (e) => {
        const selectedFormat = e.target.value.toUpperCase(); // Ensure UPPERCASE
        setFormatType(selectedFormat);
        setFormData((prev) => ({
            ...prev,
            format_type: selectedFormat, // Ensure consistency
        }));
    };

    return (
        <div className="config-container">
            <h2>💾 Local Storage Configuration</h2>
            <p>Specify where the ingested data should be saved.</p>

            <label>🗄️ Output Path:</label>
            <input
                type="text"
                name="outputPath"
                value={formData.output_path || ""}
                onChange={handleChange}
                placeholder="/path/to/save"
            />

            <label>📄 Format Type:</label>
            <select name="format_type" value={formData.format_type || ""} onChange={handleFormatChange}>
                <option value="">Select Format</option>
                <option value="JSON">JSON</option>
                <option value="CSV">CSV</option>
            </select>
        </div>
    );
};

export default LocalStorageConfig;
