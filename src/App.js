import './App.css';
import { useState } from 'react';
import { FaCloudUploadAlt } from 'react-icons/fa';

function App() {
  const [fileName, setFileName] = useState('No file selected');
  const [selectedFile, setSelectedFile] = useState(null);
  const [responseData, setResponseData] = useState(null);
  const [scrapeData, setScrapeData] = useState(null);
  const [urlMetricsLoading, setUrlMetricsLoading] = useState(false); // Separate loader for URL Metrics
  const [googleSheetLoading, setGoogleSheetLoading] = useState(false); // Separate loader for Google Sheet
  const [searchQuery, setSearchQuery] = useState('');
  const backendUrl = 'http://127.0.0.1:5000'; // Your backend URL

  const updateFileName = (file) => {
    setFileName(file ? file.name : 'No file selected');
    setSelectedFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    updateFileName(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    updateFileName(file);
  };

  const handleScrapeData = async () => {
    if (!selectedFile) {
      alert('Please select a file first.');
      return;
    }

    setUrlMetricsLoading(true); // Set URL Metrics loader

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${backendUrl}/fetch_url_metrics_csv`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        const flattenedData = data.flatMap((item) => item.results);
        setResponseData(flattenedData);
        alert('Data scraped successfully!');
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.error} - ${errorData.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setUrlMetricsLoading(false); // Reset URL Metrics loader
    }
  };

  const handleGoogleSheetScrape = async () => {
    setGoogleSheetLoading(true); // Set Google Sheet loader

    try {
      const response = await fetch(`${backendUrl}/start-scrape`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        const transformedData = data.domains.map((domain) => ({ domain }));
        setScrapeData(transformedData);
        alert('Google Sheet data scraped successfully!');
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.error} - ${errorData.message}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setGoogleSheetLoading(false); // Reset Google Sheet loader
    }
  };

  const urlMetricsColumns = [
    { key: 'page', header: 'Page' },
    { key: 'subdomain', header: 'Subdomain' },
    { key: 'root_domain', header: 'Root Domain' },
    { key: 'page_authority', header: 'Page Authority' },
    { key: 'domain_authority', header: 'Domain Authority' },
    { key: 'spam_score', header: 'Spam Score' },
  ];

  const googleSheetColumns = [
    { key: 'domain', header: 'Domain Name' },
  ];

  const downloadCSV = (data, filename) => {
    if (!data || data.length === 0) {
      alert('No data available to download.');
      return;
    }

    const headers = Object.keys(data[0]);
    const csvRows = [];
    csvRows.push(headers.join(','));

    data.forEach((row) => {
      const values = headers.map((header) => {
        const value = row[header] ?? '';
        return `"${value.toString().replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(','));
    });

    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'data.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  // Filter data based on the search query
  const filteredData = responseData?.filter((row) => {
    return urlMetricsColumns.some((col) =>
      String(row[col.key] || '').toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  // Filter data based on the search query
  const filteredScrapeData = scrapeData?.filter((row) => {
    return googleSheetColumns.some((col) =>
      String(row[col.key] || '').toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  return (
    <div className="App">
      <div className="scrape-container">
        <button
          className="scrape-btn"
          id="scrapeBtn"
          onClick={handleScrapeData}
          disabled={urlMetricsLoading} // Disable only when URL Metrics is loading
        >
          {urlMetricsLoading ? 'Fetching Url Metrics...' : 'Get Url Metrics'}
        </button>
        <button
          className="scrape-btn"
          id="googleSheetScrapeBtn"
          onClick={handleGoogleSheetScrape}
          disabled={googleSheetLoading} // Disable only when Google Sheet is loading
          style={{ marginLeft: '10px' }}
        >
          {googleSheetLoading ? 'Scraping Google Sheet...' : 'Scrape Google Sheet'}
        </button>
      </div>

      {/* URL Metrics Loader */}
      {urlMetricsLoading && (
        <div className="loader-container">
          <div className="spinner"></div>
          <p>Loading URL Metrics...</p>
        </div>
      )}

      {/* Google Sheet Loader */}
      {googleSheetLoading && (
        <div className="loader-container">
          <div className="spinner"></div>
          <p>Loading Google Sheet Data...</p>
        </div>
      )}

      {/* Display for URL Metrics data */}
      <div id="dataContainer" className="data-container">
        {responseData && responseData.length > 0 ? (
          <div className="table-wrapper">
            <h2>URL Metrics Data</h2>
            {/* Search Input */}
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ marginBottom: '10px', padding: '5px',  marginRight: '15px' }}
            />
            <button
              className="download-btn"
              onClick={() => downloadCSV(responseData, 'url_metrics_data.csv')}
              style={{ marginBottom: '10px', padding: '5px' }}
            >
              Download URL Metrics as CSV
            </button>
            <table className="data-table">
              <thead>
                <tr>
                  {urlMetricsColumns.map((col) => (
                    <th key={col.key}>{col.header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {/* {responseData.map((row, index) => (
                  <tr key={index}>
                    {urlMetricsColumns.map((col) => (
                      <td key={col.key}>{row[col.key] || '-'}</td>
                    ))}
                  </tr>
                ))} */}
              {filteredData.length > 0 ? (
                filteredData.map((row, index) => (
                  <tr key={index}>
                    {urlMetricsColumns.map((col) => (
                      <td key={col.key}>{row[col.key] || '-'}</td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={urlMetricsColumns.length}>No matching data found</td>
                </tr>
              )}
              </tbody>
            </table>
          </div>
        ) : (
          responseData && <p>No URL metrics data available to display.</p>
        )}
      </div>

      {/* Display for Google Sheet scrape data */}
      <div id="scrapeDataContainer" className="data-container">
        {scrapeData && scrapeData.length > 0 ? (
          <div className="table-wrapper">
            <h2>Google Sheet Data</h2>
            {/* Search Input */}
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ marginBottom: '10px', padding: '5px', marginRight: '15px' }}
          />
            <button
              className="download-btn"
              onClick={() => downloadCSV(scrapeData, 'google_sheet_data.csv')}
              style={{ marginBottom: '10px', padding: '5px' }}
            >
              Download Google Sheet Data as CSV
            </button>
            <table className="data-table">
              <thead>
                <tr>
                  {googleSheetColumns.map((col) => (
                    <th key={col.key}>{col.header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {/* {scrapeData.map((row, index) => (
                  <tr key={index}>
                    {googleSheetColumns.map((col) => (
                      <td key={col.key}>{row[col.key] || '-'}</td>
                    ))}
                  </tr>
                ))} */}

              {filteredScrapeData.length > 0 ? (
                filteredScrapeData.map((row, index) => (
                  <tr key={index}>
                    {googleSheetColumns.map((col) => (
                      <td key={col.key}>{row[col.key] || '-'}</td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={googleSheetColumns.length}>No matching data found</td>
                </tr>
              )}
              </tbody>
            </table>
          </div>
        ) : (
          scrapeData && <p>No Google Sheet data available to display.</p>
        )}
      </div>

      <div className="upload-container">
        <h1 className="upload-area">Upload your file</h1>
        <div
          className="drop-zone"
          id="dropZone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="fileInput"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".csv, .xlsx"
          />
          <div
            className="upload-icon"
            onClick={() => document.getElementById('fileInput').click()}
          >
            <FaCloudUploadAlt size={30} />
          </div>
          <p>Drag & drop any file here (CSV or XLSX)</p>
        </div>
        <p className="file-name" id="fileName">{fileName}</p>
      </div>
    </div>
  );
}

export default App;