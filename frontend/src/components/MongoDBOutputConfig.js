import React, { useState, useEffect } from "react";
import "./DBConfig.css";

const MongoDBOutputConfig = ({ formData, setFormData }) => {
    const defaultPort = 27017; // Default MongoDB Port

    const [localConfig, setLocalConfig] = useState({
        host: formData.host || "",
        port: formData.port || defaultPort,
        username: formData.username || "",
        password: formData.password || "",
        database: formData.database || "",
    });

    // Ensure port is always included in the form data
    useEffect(() => {
        setFormData((prev) => ({
            ...prev,
            port: prev.port ? parseInt(prev.port, 10) : defaultPort, // Ensure integer port
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
            <h2>🍃 MongoDB Output Configuration</h2>
            <div className="db-input-group">
                <label>Host:</label>
                <input type="text" name="host" value={localConfig.host} onChange={handleChange} placeholder="e.g., localhost or 192.168.1.1" />
            </div>
            <div className="db-input-group">
                <label>Port:</label>
                <input type="number" name="port" value={localConfig.port} onChange={handleChange} placeholder="27017 (default)" />
            </div>
            <div className="db-input-group">
                <label>Username:</label>
                <input type="text" name="username" value={localConfig.username} onChange={handleChange} placeholder="MongoDB Username" />
            </div>
            <div className="db-input-group">
                <label>Password:</label>
                <input type="password" name="password" value={localConfig.password} onChange={handleChange} placeholder="••••••••" />
            </div>
            <div className="db-input-group">
                <label>Database Name:</label>
                <input type="text" name="database" value={localConfig.database} onChange={handleChange} placeholder="Database Name" />
            </div>
        </div>
    );
};

export default MongoDBOutputConfig;
