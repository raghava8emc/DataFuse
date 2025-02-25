import React from "react";
import "./SourceSelection.css";

const sources = [
    { id: "restapi", name: "REST API", icon: "🌐", description: "Fetch data from online APIs" },
    { id: "sftp", name: "SFTP", icon: "📂", description: "Download data from SFTP server" },
    { id: "mysql", name: "MySQL", icon: "🗄️", description: "Extract data from MySQL database" },
    { id: "postgresql", name: "PostgreSQL", icon: "🐘", description: "Connect to PostgreSQL database" },
    { id: "mongodb", name: "MongoDB", icon: "🍃", description: "Retrieve data from MongoDB collections" },
];

const SourceSelection = ({ selectedSource, setSelectedSource }) => {
    const handleSelect = (source) => {
        if (typeof setSelectedSource === "function") {
            setSelectedSource(source);
        } else {
            console.warn("setSelectedSource is not a function!");
        }
    };

    return (
        <div className="selection-container">
            <h2>Select Data Source</h2>
            <div className="source-list">
                {sources.map((source) => (
                    <button
                        key={source.id}
                        className={`source-button ${selectedSource === source.id ? "active" : ""}`}
                        onClick={() => handleSelect(source.id)}
                        title={source.description}
                    >
                        {source.icon} {source.name}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default SourceSelection;
