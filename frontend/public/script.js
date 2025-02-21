document.getElementById("nextToConfig").addEventListener("click", function() {
    let sourceType = document.getElementById("sourceType").value;

    // Hide all configurations initially
    document.getElementById("restApiConfig").classList.add("hidden");
    document.getElementById("sftpConfig").classList.add("hidden");
    document.getElementById("dbInputConfig").classList.add("hidden");

    // Show the relevant input source configuration
    if (sourceType === "restapi") {
        document.getElementById("restApiConfig").classList.remove("hidden");
    } else if (sourceType === "sftp") {
        document.getElementById("sftpConfig").classList.remove("hidden");
    } else if (["mysql", "postgresql", "mongodb"].includes(sourceType)) {
        document.getElementById("dbInputConfig").classList.remove("hidden");
    }

    // Move to the next step
    document.getElementById("step3").classList.remove("hidden");
});

document.getElementById("nextToOutput").addEventListener("click", function() {
    let storageType = document.getElementById("storageType").value;

    // Ensure storage config is visible
    document.getElementById("outputConfig").classList.remove("hidden");

    if (storageType === "local") {
        document.getElementById("localConfig").classList.remove("hidden");
        document.getElementById("dbConfigOutput").classList.add("hidden");
    } else {
        document.getElementById("localConfig").classList.add("hidden");
        document.getElementById("dbConfigOutput").classList.remove("hidden");
    }

    // Show the submit button after everything is configured
    document.getElementById("submitBtn").classList.remove("hidden");
});

document.getElementById("ingestForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent page reload

    const sourceType = document.getElementById("sourceType").value;
    let requestData = {
        source_type: sourceType,
        config: {},
        storage_type: "",
        format_type: "",
        output_config: {}
    };

    // Handle source type configurations
    if (sourceType === "restapi") {
        requestData.config = {
            base_url: document.getElementById("baseUrl").value,
            headers: { "Content-Type": document.getElementById("contentType").value },
            endpoints: document.getElementById("endpoints").value.split(",").map(e => e.trim())
        };
    } else if (sourceType === "sftp") {
        requestData.config = {
            host: document.getElementById("sftpHost").value,
            port: parseInt(document.getElementById("sftpPort").value),
            username: document.getElementById("sftpUsername").value,
            password: document.getElementById("sftpPassword").value,
            remote_path: document.getElementById("remotePath").value,
            file_patterns: Array.from(document.getElementById("filePatterns").selectedOptions).map(opt => opt.value)
        };
    } else if (["mysql", "postgresql", "mongodb"].includes(sourceType)) {
        requestData.config = {
            host: document.getElementById("dbInputHost").value,
            port: parseInt(document.getElementById("dbInputPort").value),
            username: document.getElementById("dbInputUser").value,
            password: document.getElementById("dbInputPassword").value,
            database: document.getElementById("dbInputName").value,
            table_names: document.getElementById("dbInputTables").value.split(",").map(e => e.trim())
        };
    }

    // Handle storage type configurations
    requestData.storage_type = document.getElementById("storageType").value.toUpperCase();

    if (requestData.storage_type === "LOCAL") {
        requestData.format_type = document.getElementById("formatType").value.toUpperCase();
        requestData.output_config.output_path = document.getElementById("outputPath").value;
    } else {
        requestData.format_type = "JSON"; // Databases only support JSON for now
        requestData.output_config = {
            host: document.getElementById("dbHost").value,
            port: parseInt(document.getElementById("dbPort").value),
            username: document.getElementById("dbUser").value,
            password: document.getElementById("dbPassword").value,
            database: document.getElementById("dbName").value
        };
    }

    console.log("Sending request:", requestData);

    try {
        const response = await fetch("http://localhost:8000/ingest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();
        alert(`Success: ${result.message}`);
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error("Submission Error:", error);
    }
});
