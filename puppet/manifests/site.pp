# ========================================================
# site.pp - Puppet Configuration Management & Node Compliance
# Enforces enterprise standards across staging and production hosts
# ========================================================

node default {
  include role::app_server
}

node 'staging-agent-node-01.buildforge.corp' {
  include profile::base_security
  include profile::java_environment
  include profile::docker_daemon
  include profile::firewall_rules
}

# --- Profile: Java 17 & Maven Toolchain ---
class profile::java_environment {
  package { 'openjdk-17-jdk':
    ensure => 'installed',
  }

  package { 'maven':
    ensure  => 'installed',
    require => Package['openjdk-17-jdk'],
  }

  file { '/etc/profile.d/maven.sh':
    ensure  => 'file',
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => "export MAVEN_HOME=/usr/share/maven\nexport PATH=\$PATH:\$MAVEN_HOME/bin\n",
  }
}

# --- Profile: Docker Engine & Security Hardening ---
class profile::docker_daemon {
  package { 'docker.io':
    ensure => 'installed',
  }

  service { 'docker':
    ensure     => 'running',
    enable     => true,
    hasrestart => true,
    require    => Package['docker.io'],
  }

  user { 'jenkins':
    ensure  => 'present',
    groups  => ['docker'],
    require => Package['docker.io'],
  }
}

# --- Profile: Security & Firewall Compliance ---
class profile::firewall_rules {
  # Enforce iptables / ufw baseline
  package { 'ufw':
    ensure => 'installed',
  }

  service { 'ufw':
    ensure  => 'running',
    enable  => true,
    require => Package['ufw'],
  }

  # Allow inbound HTTP, Ingress (8090), and App (8085)
  exec { 'allow-http':
    command => '/usr/sbin/ufw allow 80/tcp',
    unless  => '/usr/sbin/ufw status | grep "80/tcp.*ALLOW"',
  }

  exec { 'allow-ingress-8090':
    command => '/usr/sbin/ufw allow 8090/tcp',
    unless  => '/usr/sbin/ufw status | grep "8090/tcp.*ALLOW"',
  }

  exec { 'allow-app-8085':
    command => '/usr/sbin/ufw allow 8085/tcp',
    unless  => '/usr/sbin/ufw status | grep "8085/tcp.*ALLOW"',
  }
}
