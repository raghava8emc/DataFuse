document.getElementById("nextToUrl").addEventListener("click", function() {
    document.getElementById("step2").classList.remove("hidden");
});

document.getElementById("nextToStorage").addEventListener("click", function() {
    document.getElementById("step3").classList.remove("hidden");
});

document.getElementById("nextToConfig").addEventListener("click", function() {
    let storageType = document.getElementById("storageType").value;
    document.getElementById("storageConfig").classList.remove("hidden");

    if (storageType === "local") {
        document.getElementById("localConfig").classList.remove("hidden");
        document.getElementById("dbConfig").classList.add("hidden");
    } else {
        document.getElementById("localConfig").classList.add("hidden");
        document.getElementById("dbConfig").classList.remove("hidden");
    }

    checkSubmitVisibility();
});

document.getElementById("ingestForm").addEventListener("input", checkSubmitVisibility);

function checkSubmitVisibility() {
    let storageType = document.getElementById("storageType").value;
    let submitBtn = document.getElementById("submitBtn");

    if (storageType === "local") {
        let formatSelected = document.getElementById("formatType").value;
        let pathFilled = document.getElementById("outputPath").value.trim() !== "";
        
        submitBtn.classList.toggle("hidden", !(formatSelected && pathFilled));
    } else {
        let requiredFields = ["dbHost", "dbPort", "dbUser", "dbPassword", "dbName"];
        let allFilled = requiredFields.every(id => document.getElementById(id).value.trim() !== "");
        
        submitBtn.classList.toggle("hidden", !allFilled);
    }
}

document.getElementById("ingestForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const sourceType = document.getElementById("sourceType").value;
    const baseUrl = document.getElementById("baseUrl").value;
    const endpoints = document.getElementById("endpoints").value.split(",").map(e => e.trim());
    const contentType = document.getElementById("contentType").value;
    const storageType = document.getElementById("storageType").value;

    let requestData = {
        source_type: sourceType,
        config: {
            base_url: baseUrl,
            headers: {
                "Content-Type": contentType
            },
            endpoints: endpoints
        },
        storage_type: storageType.toUpperCase(),
        format_type: "JSON",
        output_config: {},
        validation_schema: {}
    };

    if (storageType === "local") {
        requestData.format_type = document.getElementById("formatType").value;
        requestData.output_config["output_path"] = document.getElementById("outputPath").value;
    } else {
        requestData.output_config = {
            host: document.getElementById("dbHost").value,
            port: parseInt(document.getElementById("dbPort").value),
            username: document.getElementById("dbUser").value,
            password: document.getElementById("dbPassword").value,
            database: document.getElementById("dbName").value,
            table_names: {}
        };
        endpoints.forEach(endpoint => {
            requestData.output_config.table_names[endpoint] = `${endpoint}_data`;
        });
    }

    console.log("Sending request:", requestData);

    try {
        const response = await fetch("http://localhost:8000/ingest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();
        alert(`Success: ${result.message}`);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});
