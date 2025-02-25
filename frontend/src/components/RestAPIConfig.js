import React, { useState } from "react";
import "./RestAPIConfig.css"; // Add styling here

const RestAPIConfig = ({ formData, setFormData }) => {
    const [baseUrl, setBaseUrl] = useState(formData.base_url || ""); // Fix naming
    const [endpoints, setEndpoints] = useState(formData.endpoints?.join(", ") || ""); // Convert array to string
    const [contentType, setContentType] = useState(formData.headers?.["Content-Type"] || "application/json"); // Fix headers

    const handleInputChange = (setter, field, value) => {
        setter(value);
        setFormData((prev) => ({
            ...prev,
            ...(field === "base_url"
                ? { base_url: value }
                : field === "endpoints"
                ? { endpoints: value.split(",").map((e) => e.trim()) } 
                : field === "contentType"
                ? { headers: { ...prev.headers, "Content-Type": value } } 
                : { [field]: value })
        }));
    };

    return (
        <div className="rest-api-config">
            <h2>🌐 Configure REST API</h2>

            <div className="form-group">
                <label htmlFor="baseUrl">🔗 Base URL:</label>
                <input
                    type="text"
                    id="baseUrl"
                    placeholder="https://example.com"
                    value={baseUrl}
                    onChange={(e) => handleInputChange(setBaseUrl, "base_url", e.target.value)}
                />
            </div>

            <div className="form-group">
                <label htmlFor="endpoints">📌 Endpoints (comma-separated):</label>
                <input
                    type="text"
                    id="endpoints"
                    placeholder="posts, comments, albums"
                    value={endpoints}
                    onChange={(e) => handleInputChange(setEndpoints, "endpoints", e.target.value)}
                />
            </div>

            <div className="form-group">
                <label htmlFor="contentType">📝 Content Type:</label>
                <select
                    id="contentType"
                    value={contentType}
                    onChange={(e) => handleInputChange(setContentType, "contentType", e.target.value)}
                >
                    <option value="application/json">JSON</option>
                    <option value="text/xml">XML</option>
                    <option value="text/csv">CSV</option>
                    <option value="application/x-ndjson">NDJSON</option>
                </select>
            </div>
        </div>
    );
};

export default RestAPIConfig;
