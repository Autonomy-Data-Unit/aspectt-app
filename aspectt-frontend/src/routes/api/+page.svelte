<script lang="ts">
	const origin = (typeof window !== 'undefined') ? window.location.origin : 'https://aspectt.apps.autonomy.work';
	const baseUrl = `${origin}/api`;

	const endpoints = [
		{
			method: 'GET',
			path: '/api/occupations',
			desc: 'List/search occupations',
			params: 'q (search query), major_group, limit, offset',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}',
			desc: 'Get full occupation detail by UK SOC 2020 code',
			params: 'soc_code (e.g. 2134)',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/skills',
			desc: 'Get skills data for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/abilities',
			desc: 'Get abilities data for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/knowledge',
			desc: 'Get knowledge data for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/tasks',
			desc: 'Get task statements for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/technology-skills',
			desc: 'Get technology skills for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/work-activities',
			desc: 'Get work activities for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/work-context',
			desc: 'Get work context for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/work-styles',
			desc: 'Get work styles for an occupation',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/interests',
			desc: 'Get interests data',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/work-values',
			desc: 'Get work values data',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/education',
			desc: 'Get education/training data',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/occupations/{soc_code}/related',
			desc: 'Get related occupations',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/crosswalk',
			desc: 'Get the US O*NET → UK SOC crosswalk',
			params: 'uk_soc, onet_soc, limit, offset',
		},
		{
			method: 'GET',
			path: '/api/browse/major-groups',
			desc: 'Get all SOC major groups',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/browse/job-zones',
			desc: 'Get occupations grouped by job zone',
			params: '',
		},
		{
			method: 'GET',
			path: '/api/stats',
			desc: 'Get dataset statistics',
			params: '',
		},
	];
</script>

<div class="container">
	<h1 class="page-title">ASPECTT public API</h1>
	<p class="page-desc">
		All endpoints return JSON. Base URL: <code>{baseUrl}</code>
	</p>

	<div class="card">
		<h2>Interactive documentation</h2>
		<p>
			Visit <a href="{origin}/docs" target="_blank">{origin}/docs</a>
			for the auto-generated Swagger UI with try-it-out functionality.
		</p>
	</div>

	<div class="card">
		<h2>Endpoints</h2>
		<div class="endpoints">
			{#each endpoints as ep}
				<div class="endpoint">
					<div class="ep-header">
						<span class="method">{ep.method}</span>
						<code class="path">{ep.path}</code>
					</div>
					<p class="ep-desc">{ep.desc}</p>
					{#if ep.params}
						<p class="ep-params"><strong>Parameters:</strong> {ep.params}</p>
					{/if}
				</div>
			{/each}
		</div>
	</div>

	<div class="card license-card">
		<h2>License</h2>
		<p>
			<a href="https://creativecommons.org/licenses/by-nc/4.0/" target="_blank" rel="noopener license">
				<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" />
			</a>
		</p>
		<p>
			ASPECTT data is licensed under a
			<a href="https://creativecommons.org/licenses/by-nc/4.0/" target="_blank" rel="noopener license">Creative Commons Attribution-NonCommercial 4.0 International License</a>.
			You are free to share and adapt the data for non-commercial purposes, provided you give appropriate credit.
		</p>
	</div>

	<div class="card">
		<h2>Example</h2>
		<pre><code>curl "{baseUrl}/occupations?q=software&limit=5"

curl "{baseUrl}/occupations/2134"

curl "{baseUrl}/occupations/2134/skills"</code></pre>
	</div>
</div>

<style>
	.page-desc code {
		background: var(--color-bg);
		padding: 0.2rem 0.5rem;
		border-radius: 5px;
		font-size: 0.8125rem;
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		border: 1px solid var(--color-border);
	}

	.endpoints {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.endpoint {
		padding: 0.875rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		transition: border-color var(--transition);
	}

	.endpoint:hover {
		border-color: var(--color-border-hover);
	}

	.ep-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.3rem;
	}

	.method {
		font-size: 0.6875rem;
		font-weight: 700;
		padding: 0.2rem 0.5rem;
		background: var(--color-success);
		color: white;
		border-radius: 4px;
		letter-spacing: 0.03em;
	}

	.path {
		font-size: 0.875rem;
		font-weight: 500;
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
	}

	.ep-desc {
		font-size: 0.8125rem;
		color: var(--color-text-secondary);
	}

	.ep-params {
		font-size: 0.8rem;
		color: var(--color-text-secondary);
		margin-top: 0.25rem;
	}

	pre {
		background: var(--color-primary);
		color: #a0d2db;
		padding: 1.25rem;
		border-radius: var(--radius-lg);
		overflow-x: auto;
		font-size: 0.8125rem;
		line-height: 1.7;
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		border: 1px solid rgba(255, 255, 255, 0.06);
	}
</style>
