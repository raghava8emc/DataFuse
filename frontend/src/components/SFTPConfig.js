import React, { useState } from "react";
import "./SFTPConfig.css";

const SFTPConfig = ({ formData, setFormData }) => {
    const [localConfig, setLocalConfig] = useState({
        host: formData.host || "",
        port: formData.port || 22, // Default to 22
        username: formData.username || "",
        password: formData.password || "",
        remote_path: formData.remote_path || "",
        file_patterns: formData.file_patterns || [],
    });

    const handleChange = (e) => {
        const { name, value } = e.target;

        setLocalConfig((prev) => ({
            ...prev,
            [name]: name === "port" ? parseInt(value, 10) || 22 : value,
        }));

        setFormData((prev) => ({
            ...prev,
            [name]: name === "port" ? parseInt(value, 10) || 22 : value,
        }));
    };

    return (
        <div className="sftp-config-container">
            <h2>📂 SFTP Configuration</h2>
            <p>Enter the details to connect to your SFTP server.</p>

            <div className="form-group">
                <label>🔗 Host:</label>
                <input
                    type="text"
                    name="host"
                    value={localConfig.host}
                    onChange={handleChange}
                    placeholder="sftp.example.com"
                />
            </div>

            <div className="form-group">
                <label>🔢 Port:</label>
                <input
                    type="number"
                    name="port"
                    value={localConfig.port}
                    onChange={handleChange}
                    placeholder="22 (default)"
                />
            </div>

            <div className="form-group">
                <label>👤 Username:</label>
                <input
                    type="text"
                    name="username"
                    value={localConfig.username}
                    onChange={handleChange}
                    placeholder="your_username"
                />
            </div>

            <div className="form-group">
                <label>🔑 Password:</label>
                <input
                    type="password"
                    name="password"
                    value={localConfig.password}
                    onChange={handleChange}
                    placeholder="your_password"
                />
            </div>

            <div className="form-group">
                <label>📁 Remote Path:</label>
                <input
                    type="text"
                    name="remote_path"
                    value={localConfig.remote_path}
                    onChange={handleChange}
                    placeholder="/remote/data/"
                />
            </div>

            <div className="form-group">
                <label>📂 File Patterns:</label>
                <select
                    multiple
                    name="file_patterns"
                    value={localConfig.file_patterns}
                    onChange={(e) => {
                        const selectedOptions = Array.from(e.target.selectedOptions, (option) => option.value);
                        setLocalConfig({ ...localConfig, file_patterns: selectedOptions });
                        setFormData({ ...formData, file_patterns: selectedOptions });
                    }}
                >
                    <option value="*">All Files (*)</option>
                    <option value="*.json">JSON</option>
                    <option value="*.csv">CSV</option>
                    <option value="*.xml">XML</option>
                    <option value="*.txt">Text</option>
                </select>
            </div>
        </div>
    );
};

export default SFTPConfig;
