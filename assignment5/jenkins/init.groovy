import jenkins.model.JenkinsLocationConfiguration

// start.sh supplies the HTTPS URL of the private Codespaces forwarded port.
// Local compose does not set this variable and keeps its existing location.
def publicUrl = System.getenv('JENKINS_PUBLIC_URL')?.trim()
if (publicUrl) {
    def location = JenkinsLocationConfiguration.get()
    location.setUrl(publicUrl.endsWith('/') ? publicUrl : publicUrl + '/')
    location.save()
    println('Configured Jenkins Location from JENKINS_PUBLIC_URL.')
}
