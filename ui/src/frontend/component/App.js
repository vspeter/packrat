import React from 'react';
import { Layout, NavDrawer, Panel, Sidebar, Chip, FontIcon, AppBar, Navigation, Button } from 'react-toolbox';
import { BrowserRouter as Router, Route, Link } from 'react-router-dom';
import Home from './Home';
import Repo from './Repo';
import Mirror from './Mirror';
import Package from './Package';

class App extends React.Component
{
  state = {
    leftDrawerVisable: true,
  };

  constructor()
  {
    super();
    this.packrat = new Packrat( 'http://127.0.0.1:8888' );
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
            <Link to="/repos"><Button icon="storage">Repos</Button></Link>
            <Link to="/mirrors"><Button icon="dvr">Mirrors</Button></Link>
            <Link to="/packages"><Button icon="folder">Packages</Button></Link>
          </Navigation>
        </NavDrawer>
        <Panel>
          <AppBar title="Packrat" leftIcon="menu" rightIcon="face" onLeftIconClick={ this.menuClick }>
            <Chip><Button icon='settings' disabled /></Chip>
          </AppBar>
          <div ref="content">
            <Route exact={true} path="/" component={ Home }/>
            <Route path="/repo/:id" render={ ( { match } ) => ( <Repo id={ match.params.id } getDetail={ this.packrat.getRepo } /> ) } />
            <Route exact={true} path="/repos" render={ () => ( <Repo listGet={ this.packrat.getRepoList } /> ) } />
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
