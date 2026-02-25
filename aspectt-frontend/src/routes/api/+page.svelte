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
	<h1 class="page-title">ASPECTT Public API</h1>
	<p class="page-desc">
		Access UK occupation data programmatically. All endpoints return JSON. Base URL:
		<code>{baseUrl}</code>
	</p>

	<div class="card">
		<h2>Interactive Documentation</h2>
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

	<div class="card">
		<h2>Example</h2>
		<pre><code>curl {baseUrl}/occupations?q=software&limit=5

curl {baseUrl}/occupations/2134

curl {baseUrl}/occupations/2134/skills</code></pre>
	</div>
</div>

<style>
	.page-title {
		font-size: 1.75rem;
		color: var(--color-primary);
		margin-bottom: 0.25rem;
	}

	.page-desc {
		color: var(--color-text-secondary);
		margin-bottom: 1.5rem;
	}

	.page-desc code {
		background: var(--color-bg);
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
		font-size: 0.85rem;
	}

	.endpoints {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.endpoint {
		padding: 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
	}

	.ep-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.25rem;
	}

	.method {
		font-size: 0.75rem;
		font-weight: 700;
		padding: 0.15rem 0.5rem;
		background: var(--color-success);
		color: white;
		border-radius: 4px;
	}

	.path {
		font-size: 0.9rem;
		font-weight: 500;
	}

	.ep-desc {
		font-size: 0.85rem;
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
		padding: 1rem;
		border-radius: var(--radius);
		overflow-x: auto;
		font-size: 0.85rem;
		line-height: 1.6;
	}
</style>
