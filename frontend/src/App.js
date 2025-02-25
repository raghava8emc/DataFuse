import React, { useState } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


import SourceSelection from "./components/SourceSelection";
import RestAPIConfig from "./components/RestAPIConfig";
import SFTPConfig from "./components/SFTPConfig";
import MySQLConfig from "./components/MySQLConfig";
import PostgreSQLConfig from "./components/PostgreSQLConfig";
import MongoDBConfig from "./components/MongoDBConfig";
import StorageSelection from "./components/StorageSelection";
import LocalStorageConfig from "./components/LocalStorageConfig";
import MySQLOutputConfig from "./components/MySQLOutputConfig";
import PostgreSQLOutputConfig from "./components/PostgreSQLOutputConfig";
import MongoDBOutputConfig from "./components/MongoDBOutputConfig";
import "./styles.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const App = () => {
    const [selectedSource, setSelectedSource] = useState(""); 
    const [sourceConfig, setSourceConfig] = useState({}); 
    const [showConfig, setShowConfig] = useState(false);
    const [selectedStorage, setSelectedStorage] = useState(""); 
    const [storageConfig, setStorageConfig] = useState({});
    const [formatType, setFormatType] = useState("");

    const [validationStatus, setValidationStatus] = useState(null);
    const [validationMessage, setValidationMessage] = useState(""); 
    const [isIngestionRunning, setIsIngestionRunning] = useState(false);
    const [processLogs, setProcessLogs] = useState([]);

    // Handle Source Selection
    const handleSourceSelection = (source) => {
        setSelectedSource(source);
        setSourceConfig({});
        setShowConfig(true);
        setSelectedStorage("");
        setValidationStatus(null);
        setValidationMessage("");
    };

    // Handle Storage Selection
    const handleStorageSelection = (storage) => {
        setSelectedStorage(storage);
        setStorageConfig({});
        setValidationStatus(null);
        setValidationMessage("");
    };

    // Construct Request Payload Dynamically
    const getRequestPayload = () => {
        let config = {};

        if (selectedSource === "restapi") {
            config = {
                base_url: sourceConfig.base_url || "",
                headers: sourceConfig.headers || {},
                endpoints: sourceConfig.endpoints || []
            };
        } else if (selectedSource === "sftp") {
            config = {
                host: sourceConfig.host || "",
                port: parseInt(sourceConfig.port, 10) || 22,
                username: sourceConfig.username || "",
                password: sourceConfig.password || "",
                remote_path: sourceConfig.remote_path || "",
                file_patterns: sourceConfig.file_patterns || []
            };
        } else if (selectedSource === "mysql" || selectedSource === "postgresql") {
            config = {
                host: sourceConfig.host || "",
                port: parseInt(sourceConfig.port, 10) || 3306,
                username: sourceConfig.username || "",
                password: sourceConfig.password || "",
                database: sourceConfig.database || "",
                table_names: sourceConfig.table_names ? sourceConfig.table_names.split(",").map(t => t.trim()) : []
            };
        } else if (selectedSource === "mongodb") {
            config = {
                host: sourceConfig.host || "",
                port: parseInt(sourceConfig.port, 10) || 27017,
                username: sourceConfig.username || "",
                password: sourceConfig.password || "",
                database: sourceConfig.database || "",
                collection_names: sourceConfig.collection_names ? sourceConfig.collection_names.split(",").map(c => c.trim()) : []
            };
        }

        return {
            source_type: selectedSource,
            config: config,
            storage_type: selectedStorage.toUpperCase(),
            format_type: formatType.toUpperCase() || "JSON",
            output_config: { ...storageConfig },
            validation_schema: {}
        };
    };

    const logStatus = (message, type = "info") => {
      setProcessLogs(prev => [...prev, { message, timestamp: new Date().toLocaleTimeString() }]);
      toast[type](message);
    };

    // 🔹 Step 1: Validate Before Ingestion
    const handleValidate = async () => {
        setValidationStatus("validating");
        logStatus("🔍 Validation started...", "info");
    
        const requestData = getRequestPayload();
        const startTime = Date.now();
    
        console.log("🔹 Sending Validation Request:", requestData);
    
        try {
            const response = await axios.post(`${API_BASE_URL}/validate`, requestData);
            const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);

            console.log(response)
    
            if (response.data.validation_passed) {
                setValidationStatus("success");
                setValidationMessage("");
                logStatus(`✅ Validation successful! (Time: ${elapsedTime}s)`, "success");
            } else {
                // Extract detailed error message
                const errorMsg = response.data.error || response.data.message || "Unknown validation error.";
                setValidationStatus("failed");
                setValidationMessage(errorMsg);
                logStatus(`❌ Validation failed: ${errorMsg}`, "error");
            }
        } catch (error) {
            // Handle server/network failures
            const errorMsg = error.response?.data?.error || error.response?.data?.message || "Validation failed due to a network or server issue.";
            setValidationStatus("failed");
            setValidationMessage(errorMsg);
            logStatus(`❌ Validation failed: ${errorMsg}`, "error");
        }
    };
  

    // 🔹 Step 2: Start Ingestion After Validation
    const handleStartIngestion = async () => {
        if (validationStatus !== "success") {
            logStatus("⚠️ Cannot start ingestion. Validation failed or not completed.", "warn");
            return;
        }
    
        setIsIngestionRunning(true);
        logStatus("🚀 Ingestion started...", "info");
    
        const startTime = Date.now();
        const requestData = getRequestPayload();
    
        try {
            console.log("🔹 Starting Ingestion with Data:", requestData);
            const response = await axios.post(`${API_BASE_URL}/ingest`, requestData);
    
            const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
            logStatus(`✅ Ingestion successful! (Time: ${elapsedTime}s)`, "success");
        } catch (error) {
            logStatus("❌ Ingestion failed! Check logs.", "error");
            console.error("Ingestion Error:", error);
        } finally {
            setIsIngestionRunning(false);
        }
    };
  

    return (
        <div className="page-container">
            <ToastContainer position="top-right" autoClose={3000} />
            <h1 className="title">🚀 Data Ingestion Setup</h1>

            <div className="grid-container">
                {/* Left Side: Source Selection & Config */}
                <div className="input-container">
                    <SourceSelection selectedSource={selectedSource} setSelectedSource={handleSourceSelection} />

                    {showConfig && (
                        <div className="config-section">
                            {selectedSource === "restapi" && <RestAPIConfig formData={sourceConfig} setFormData={setSourceConfig} />}
                            {selectedSource === "sftp" && <SFTPConfig formData={sourceConfig} setFormData={setSourceConfig} />}
                            {selectedSource === "mysql" && <MySQLConfig formData={sourceConfig} setFormData={setSourceConfig} />}
                            {selectedSource === "postgresql" && <PostgreSQLConfig formData={sourceConfig} setFormData={setSourceConfig} />}
                            {selectedSource === "mongodb" && <MongoDBConfig formData={sourceConfig} setFormData={setSourceConfig} />}
                        </div>
                    )}
                </div>

                {/* Right Side: Storage Selection & Config */}
                <div className="output-container">
                    <StorageSelection selectedStorage={selectedStorage} setSelectedStorage={handleStorageSelection} />

                    {selectedStorage && (
                        <div className="config-section">
                            {selectedStorage === "local" && <LocalStorageConfig formData={storageConfig} setFormData={setStorageConfig} setFormatType={setFormatType} />}
                            {selectedStorage === "mysql" && <MySQLOutputConfig formData={storageConfig} setFormData={setStorageConfig} />}
                            {selectedStorage === "postgresql" && <PostgreSQLOutputConfig formData={storageConfig} setFormData={setStorageConfig} />}
                            {selectedStorage === "mongodb" && <MongoDBOutputConfig formData={storageConfig} setFormData={setStorageConfig} />}
                        </div>
                    )}
                </div>
            </div>

            {/* 🔹 Step 5: Validation & Ingestion */}
            <div className="action-buttons">
                <button onClick={handleValidate} disabled={validationStatus === "validating"}>
                    {validationStatus === "validating" ? "Validating..." : "Validate Configuration"}
                </button>

                {validationStatus === "success" && (
                    <button onClick={handleStartIngestion} disabled={isIngestionRunning}>
                        {isIngestionRunning ? "Ingesting..." : "Start Ingestion"}
                    </button>
                )}

                {validationStatus === "failed" && (
                    <p className="error-message">❌ Validation failed! {validationMessage}</p>
                )}
            </div>
        </div>
    );
};

export default App;
