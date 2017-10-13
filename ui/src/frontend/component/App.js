import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Packrat from './Packrat';
import ServerError from './ServerError';
import Home from './Home';
import Package from './Package';
import PackageFile from './PackageFile';
import Repo from './Repo';
import Mirror from './Mirror';
import DistroVersion from './DistroVersion';
import ReleaseType from './ReleaseType';
import AddPackageFile from './AddPackageFile';


class App extends React.Component
{
  state = {
    leftDrawerVisable: true,
  };

  constructor()
  {
    super();
    this.packrat = new Packrat( 'http://127.0.0.1:8888' );
    //this.packrat = new Packrat( 'http://192.168.13.100:8888' );
    this.packrat.cinp.server_error_handler = this.serverError;
  }

  menuClick = () =>
  {
    this.setState( { leftDrawerVisable: !this.state.leftDrawerVisable} );
  };

  serverError = ( msg, trace ) =>
  {
    this.refs.serverError.show( msg, trace );
  };

  render()
  {
    return (
<Router>
  <div>
    <ServerError ref="serverError" />
    <div>
      <Layout>
        <NavDrawer pinned={this.state.leftDrawerVisable}>
          <Navigation type="vertical">
            <Link to="/"><Button icon="home">Home</Button></Link>
            <Link to="/packages"><Button icon="folder">Packages</Button></Link>
            <Link to="/mirrors"><Button icon="dvr">Mirrors</Button></Link>
            <Link to="/repos"><Button icon="storage">Repos</Button></Link>
            <Link to="/distroversions"><Button icon="group_work">Distro Versions</Button></Link>
            <Link to="/releasetypes"><Button icon="list">Release Types</Button></Link>
            <Link to="/addpackagefile"><Button icon="note_add">Add Package File</Button></Link>
          </Navigation>
        </NavDrawer>
        <Panel>
          <AppBar title="Packrat" leftIcon="menu" rightIcon="face" onLeftIconClick={ this.menuClick }>
            <Chip><Button icon='settings' disabled /></Chip>
          </AppBar>
          <div ref="content">
            <Route exact={true} path="/" component={ Home }/>
            <Route path="/package/:id" render={ ( { match } ) => ( <Package id={ match.params.id } getDetail={ this.packrat.getPackage } packrat={ this.packrat } /> ) } />
            <Route path="/packagefile/:id" render={ ( { match } ) => ( <PackageFile id={ match.params.id } getDetail={ this.packrat.getPackageFile } packrat={ this.packrat } /> ) } />
            <Route path="/repo/:id" render={ ( { match } ) => ( <Repo id={ match.params.id } getDetail={ this.packrat.getRepo } /> ) } />
            <Route path="/mirror/:id" render={ ( { match } ) => ( <Mirror id={ match.params.id } getDetail={ this.packrat.getMirror } /> ) } />
            <Route path="/distroversion/:id" render={ ( { match } ) => ( <DistroVersion id={ match.params.id } getDetail={ this.packrat.getDistroVersion } /> ) } />
            <Route path="/releasetype/:id" render={ ( { match } ) => ( <ReleaseType id={ match.params.id } getDetail={ this.packrat.getReleaseType } /> ) } />
            <Route exact={true} path="/packages" render={ () => ( <Package getList={ this.packrat.getPackageList } packrat={ this.packrat }/> ) } />
            <Route exact={true} path="/repos" render={ () => ( <Repo getList={ this.packrat.getRepoList } /> ) } />
            <Route exact={true} path="/mirrors" render={ () => ( <Mirror getList={ this.packrat.getMirrorList } /> ) } />
            <Route exact={true} path="/distroversions" render={ () => ( <DistroVersion getList={ this.packrat.getDistroVersionList } /> ) } />
            <Route exact={true} path="/releasetypes" render={ () => ( <ReleaseType getList={ this.packrat.getReleaseTypeList } /> ) } />
            <Route exact={true} path="/addpackagefile" render={ () => ( <AddPackageFile packrat={ this.packrat } /> ) } />
          </div>
        </Panel>
      </Layout>
    </div>

  </div>
</Router>
);
  }

}

export default App;
