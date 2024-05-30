// let eventSource = new EventSource('/progress');
let eventSource = {
	onmessage: () => { }
};
// let logSource = new EventSource('/logs');
let logSource = {
	onmessage: () => { }
};

document.addEventListener('DOMContentLoaded', function () {
	const loginForm = document.getElementById('login-form');
	const downloadForm = document.getElementById('download-form');
	const configForm = document.getElementById('config-form');
	const loginMessageDiv = document.getElementById('login-message');

	loginForm.addEventListener('submit', function (event) {
		event.preventDefault();
		const username = document.getElementById('login-username').value;
		const password = document.getElementById('login-password').value;

		fetch('/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		})
			.then(response => response.json())
			.then(data => {
				if (data.access_token) {
					localStorage.setItem('jwt', data.access_token);
					loginMessageDiv.style.color = 'green';
					loginMessageDiv.innerHTML = 'Login successful!';
					downloadForm.style.display = 'block';
					configForm.style.display = 'block';
					loginForm.style.display = 'none';
				} else {
					loginMessageDiv.style.color = 'red';
					loginMessageDiv.innerHTML = 'Login failed: ' + (data.error || 'Unknown error.');
				}
			});
	});

	document.getElementById('load-videos-button').addEventListener('click', function () {
		fetchUrlMap();
	});

	function fetchUrlMap() {
		const token = localStorage.getItem('jwt');
		fetch('/url_map', {
			headers: {
				'Authorization': 'Bearer ' + token
			}
		})
			.then(response => {
				if (response.ok) {
					return response.json();
				} else {
					throw new Error('Authentication failed');
				}
			})
			.then(data => {
				const urlMapList = document.getElementById('url-map-list');
				urlMapList.innerHTML = '';
				for (const [url, path] of Object.entries(data)) {
					const listItem = document.createElement('li');
					listItem.innerHTML = `<a href="/files/${path}" target="_blank">${path}</a> - <a href="${url}" target="_blank">Source</a>`;
					urlMapList.appendChild(listItem);
				}
			})
			.catch(error => {
				console.error('Error fetching URL map:', error);
			});
	}

	fetchUrlMap();

	configForm.addEventListener('submit', function (event) {
		event.preventDefault();

		const username = document.getElementById('username').value;
		const password = document.getElementById('password').value;
		const token = localStorage.getItem('jwt');

		fetch('/config', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token
			},
			body: JSON.stringify({ username, password })
		})
			.then(response => response.json())
			.then(data => {
				const messageDiv = document.getElementById('message');
				if (data.success) {
					messageDiv.style.color = 'green';
					messageDiv.innerHTML = 'Configuration saved successfully.';
				} else {
					messageDiv.style.color = 'red';
					messageDiv.innerHTML = 'Error: ' + (data.error || 'Unknown error.');
				}
				fetchUrlMap();
			});
	});

	downloadForm.addEventListener('submit', function (event) {
		event.preventDefault();

		const twitterUrl = document.getElementById('twitter-url').value;
		const token = localStorage.getItem('jwt');

		fetch('/download', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + token
			},
			body: JSON.stringify({ url: twitterUrl })
		})
			.then(response => response.json())
			.then(data => {
				const downloadMessageDiv = document.getElementById('download-message');
				if (data.success) {
					downloadMessageDiv.style.color = 'green';
					downloadMessageDiv.innerHTML = data.message;
					if (data.video_path) {
						document.getElementById('download-link').innerHTML = `<a href="/files/${data.video_path}" target="_blank">Click here to download the video</a>`;
						document.getElementById('video-container').innerHTML = `<video controls><source src="/files/${data.video_path}" type="video/mp4"></video>`;
					}
				} else {
					downloadMessageDiv.style.color = 'red';
					downloadMessageDiv.innerHTML = 'Error: ' + (data.error || 'Unknown error.');
				}
			});
	});

	eventSource.onmessage = function (event) {
		const data = JSON.parse(event.data);
		const progressDiv = document.getElementById('progress');
		const sizeDiv = document.getElementById('size');
		const downloadLinkDiv = document.getElementById('download-link');
		const videoContainerDiv = document.getElementById('video-container');

		if (progressDiv) {
			progressDiv.innerHTML = `Download progress: ${data.progress}%`;
		}
		if (sizeDiv) {
			sizeDiv.innerHTML = `Downloaded size: ${data.downloaded} / ${data.total_size} bytes`;
		}

		if (data.status === 'completed' && !document.querySelector('#video-container video')) {
			if (progressDiv) {
				progressDiv.style.color = 'green';
				progressDiv.innerHTML = 'Download completed!';
			}
			if (downloadLinkDiv) {
				downloadLinkDiv.innerHTML = `<a href="/files/${data.video_path}" target="_blank">Click here to download the video</a>`;
			}
			if (videoContainerDiv) {
				videoContainerDiv.innerHTML = `<video controls><source src="/files/${data.video_path}" type="video/mp4"></video>`;
			}
		} else if (data.status === 'error') {
			if (progressDiv) {
				progressDiv.style.color = 'red';
				progressDiv.innerHTML = 'Download failed.';
			}
		}
	};

	logSource.onmessage = function (event) {
		const logContainer = document.getElementById('log-container');
		const logMessage = document.createElement('p');
		logMessage.textContent = event.data;
		logContainer.appendChild(logMessage);
		logContainer.scrollTop = logContainer.scrollHeight;
	};

	// Close the event source connections when the window is unloaded
	window.addEventListener('beforeunload', function () {
		if (eventSource) {
			eventSource.close();
		}
		if (logSource) {
			logSource.close();
		}
		fetch('/disconnect', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ message: 'Client disconnected' }),
		});
	});

});

window.addEventListener('unload', function () {
	if (eventSource) {
		eventSource.close();
	}
	if (logSource) {
		logSource.close();
	}
});
