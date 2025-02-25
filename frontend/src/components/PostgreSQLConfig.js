import React, { useState, useEffect } from "react";
import "./DBConfig.css";

const PostgreSQLConfig = ({ formData, setFormData }) => {
    const defaultPort = 5432; // Default PostgreSQL Port

    const [localConfig, setLocalConfig] = useState({
        host: formData.host || "",
        port: formData.port || defaultPort, 
        username: formData.username || "",
        password: formData.password || "",
        database: formData.database || "",
        table_names: formData.table_names || "", 
    });

    // Ensure port is always included
    useEffect(() => {
        setFormData((prev) => ({
            ...prev,
            port: prev.port ? parseInt(prev.port, 10) : defaultPort, 
        }));
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        const updatedValue = name === "port" ? parseInt(value, 10) || defaultPort : value;

        setLocalConfig((prev) => ({
            ...prev,
            [name]: updatedValue,
        }));

        setFormData((prev) => ({
            ...prev,
            [name]: updatedValue,
        }));
    };

    return (
        <div className="db-config-container">
            <h2>🐘 PostgreSQL Configuration</h2>
            <div className="db-input-group">
                <label>🔗 Host:</label>
                <input type="text" name="host" value={localConfig.host} onChange={handleChange} />
            </div>
            <div className="db-input-group">
                <label>🔢 Port:</label>
                <input type="number" name="port" value={localConfig.port} onChange={handleChange} />
            </div>
            <div className="db-input-group">
                <label>👤 Username:</label>
                <input type="text" name="username" value={localConfig.username} onChange={handleChange} />
            </div>
            <div className="db-input-group">
                <label>🔑 Password:</label>
                <input type="password" name="password" value={localConfig.password} onChange={handleChange} />
            </div>
            <div className="db-input-group">
                <label>🏛️ Database Name:</label>
                <input type="text" name="database" value={localConfig.database} onChange={handleChange} />
            </div>
            <div className="db-input-group">
                <label>📑 Table Names (Comma-Separated):</label>
                <input type="text" name="table_names" value={localConfig.table_names} onChange={handleChange} />
            </div>
        </div>
    );
};

export default PostgreSQLConfig;
