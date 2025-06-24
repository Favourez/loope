{{/*
Expand the name of the chart.
*/}}
{{- define "emergency-response.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "emergency-response.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "emergency-response.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "emergency-response.labels" -}}
helm.sh/chart: {{ include "emergency-response.chart" . }}
{{ include "emergency-response.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "emergency-response.selectorLabels" -}}
app.kubernetes.io/name: {{ include "emergency-response.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "emergency-response.serviceAccountName" -}}
{{- if .Values.security.serviceAccount.create }}
{{- default (include "emergency-response.fullname" .) .Values.security.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.security.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the configmap
*/}}
{{- define "emergency-response.configmapName" -}}
{{- printf "%s-config" (include "emergency-response.fullname" .) }}
{{- end }}

{{/*
Create the name of the secret
*/}}
{{- define "emergency-response.secretName" -}}
{{- printf "%s-secret" (include "emergency-response.fullname" .) }}
{{- end }}

{{/*
Create the name of the PVC for app data
*/}}
{{- define "emergency-response.dataPvcName" -}}
{{- printf "%s-data-pvc" (include "emergency-response.fullname" .) }}
{{- end }}

{{/*
Create the name of the PVC for app logs
*/}}
{{- define "emergency-response.logsPvcName" -}}
{{- printf "%s-logs-pvc" (include "emergency-response.fullname" .) }}
{{- end }}

{{/*
Return the proper image name
*/}}
{{- define "emergency-response.image" -}}
{{- $registryName := .Values.global.imageRegistry -}}
{{- $repositoryName := .Values.app.image.repository -}}
{{- $tag := .Values.app.image.tag | default .Chart.AppVersion -}}
{{- if $registryName }}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else }}
{{- printf "%s:%s" $repositoryName $tag -}}
{{- end }}
{{- end }}

{{/*
Return the proper monitoring image name
*/}}
{{- define "emergency-response.monitoringImage" -}}
{{- $registryName := .Values.global.imageRegistry -}}
{{- $repositoryName := .Values.monitoring.dashboard.image.repository -}}
{{- $tag := .Values.monitoring.dashboard.image.tag | default .Chart.AppVersion -}}
{{- if $registryName }}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else }}
{{- printf "%s:%s" $repositoryName $tag -}}
{{- end }}
{{- end }}

{{/*
Return the proper nginx image name
*/}}
{{- define "emergency-response.nginxImage" -}}
{{- $registryName := .Values.global.imageRegistry -}}
{{- $repositoryName := .Values.nginx.image.repository -}}
{{- $tag := .Values.nginx.image.tag | default .Chart.AppVersion -}}
{{- if $registryName }}
{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}
{{- else }}
{{- printf "%s:%s" $repositoryName $tag -}}
{{- end }}
{{- end }}

{{/*
Return the storage class name
*/}}
{{- define "emergency-response.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass -}}
{{- else if .Values.app.persistence.storageClass }}
{{- .Values.app.persistence.storageClass -}}
{{- else }}
{{- "default" -}}
{{- end }}
{{- end }}
