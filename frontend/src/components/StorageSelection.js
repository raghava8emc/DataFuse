import React from "react";
import "./StorageSelection.css";

const storageOptions = [
    { id: "local", name: "Local Storage", icon: "💾" },
    { id: "mysql", name: "MySQL", icon: "🗄️" },
    { id: "postgresql", name: "PostgreSQL", icon: "🐘" },
    { id: "mongodb", name: "MongoDB", icon: "🍃" },
];

const StorageSelection = ({ selectedStorage, setSelectedStorage }) => {
    const handleSelect = (storage) => {
        setSelectedStorage(storage);
    };

    return (
        <div className="storage-container">
            <h2>Select Storage Destination</h2>
            <div className="storage-list">
                {storageOptions.map((storage) => (
                    <button
                        key={storage.id}
                        className={`storage-button ${selectedStorage === storage.id ? "active" : ""}`}
                        onClick={() => handleSelect(storage.id)}
                    >
                        {storage.icon} {storage.name}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default StorageSelection;
